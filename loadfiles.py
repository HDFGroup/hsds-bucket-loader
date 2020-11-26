import time
import os
import logging
import s3fs
import h5py
import h5pyd
import config
from utillib import load_file

src_bucket = config.get("src_bucket")
src_prefix = config.get("src_prefix")
src_suffix = config.get("src_suffix")
tgt_folder = config.get("tgt_folder")
tgt_bucket = config.get("tgt_bucket")
hsds_local = config.get("hsds_local")
print("hsds_local:", hsds_local)
hsds_global = config.get("hsds_global")
print("hsds_global:", hsds_global)
link_files = config.get("link_files")
print("link_files:", link_files)
username = config.get("hs_username")
password = config.get("hs_password")
inventory_domain = config.get("inventory_domain")
print("inventory_domain:", inventory_domain)
sleep_time = config.get("watchdog_sleep_time")
if "POD_NAME" in os.environ:
    pod_name = os.environ["POD_NAME"]
else:
    pod_name = ""

def ensure_folder(pathname):
    tgt_path = tgt_folder
    if not pathname.startswith(tgt_path):
        return False
    if hsds_global:
        endpoint=hsds_global
    else:
        endpoint=None
    folder = h5pyd.Folder(tgt_path, endpoint=endpoint, username=username, password=password, bucket=tgt_bucket)
    names = pathname[len(tgt_path):].split("/")
    for name in names:
        if not name:
            continue
        tgt_path = os.path.join(tgt_path, name) + '/'
        if name not in folder:
            print(f"creating folder: {tgt_path}")
            folder = h5pyd.Folder(tgt_path, mode="w", endpoint=endpoint, username=username, password=password, bucket=tgt_bucket)
    return True


def load(filename):
    verbose = True
    print(f"load_file: {filename}")
    print(f"got filename: {filename} from {inventory_domain}")
    # got filename: data/hdf5test/snp500.h5 from /home/john/bucketloader/inventory.h5
    s3path = f"s3://{src_bucket}/{filename}"
    print(f"using s3path: {s3path}")
    tgt_path = tgt_folder + filename
    print(f"tgt_path: {tgt_path}")
    ensure_folder(os.path.dirname(tgt_path))  # tbd ignore 409 errors?

    # make sure the local hsds is up (if being used)
    if hsds_local:
        endpoint = hsds_local
    else:
        endpoint = hsds_global

    print(f"running loading {s3path} to {tgt_path}")
    s3 = s3fs.S3FileSystem()

    try:
        fin = h5py.File(s3.open(s3path, "rb"), "r")
    except IOError as ioe:
        logging.error("Error opening s3path {}: {}".format(s3path, ioe))
        raise

    # create output domain
    try:
        fout = h5pyd.File(tgt_path, 'w', endpoint=endpoint, username=username, password=password, bucket=tgt_bucket)
    except IOError as ioe:
        if ioe.errno == 404:
            logging.error("Domain: {} not found".format(tgt_path))
        elif ioe.errno == 403:
            logging.error("No write access to domain: {}".format(tgt_path))
        else:
            logging.error("Error creating file {}: {}".format(tgt_path, ioe))
        raise

    # do the actual load
    try:
        if link_files:
            dataload = "link"
        else:
            dataload = "ingest"
        compression=None  # TBD
        compression_opts=None # TBD
        load_file(fin, fout, verbose=verbose, dataload=dataload, s3path=s3path, compression=compression, compression_opts=compression_opts)
    except IOError as ioe:
        logging.error("load_file error: {}".format(ioe))
        raise

    if config.get("public_read"):
        # make public read, and get acl
        print("adding public read ACL")
        acl = {"userName": "default"}
        acl["create"] = False
        acl["read"] = True
        acl["update"] = False
        acl["delete"] = False
        acl["readACL"] = True
        acl["updateACL"] = False
        fout.putACL(acl)
        
    fout.close()

    return

### main

loglevel = config.get("log_level")
logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel)

# make sure the global (and local if set) hsds is up (if being used)
for endpoint in (hsds_global, hsds_local):
    if not endpoint:
        print("local endpoint not set?")
        continue
    state = None
    while state != "READY":
        print(f"waiting on endpoint: {endpoint} to be in READY state")
        time.sleep(1)
        info = h5pyd.getServerInfo(endpoint=endpoint)
        if info and 'state' in info:
            state = info['state']
    print(f"endpoint: {endpoint} is in READY state")


f = h5pyd.File(inventory_domain, "r+", use_cache=False, endpoint=hsds_global, username=username, password=password)

table = f["inventory"]
print("table.nrows:", table.nrows)

condition = "start == 0"  # query for files that haven't been proccessed

while True:

    now = int(time.time())
    update_val = {"start": now, "status": -1, "pod_name": pod_name}


    # query for row with 0 start value and update it to now
    indices = table.update_where(condition, update_val, limit=1)
    print("indices:", indices)

    if indices is not None and len(indices) > 0:
        index = indices[0]
        print(f"getting row: {index}")
        row = table[index]
        print("got row:", row)
        filename = row[0].decode("utf-8")
        rc = 1
        try:
            load(filename)
            print(f"load({filename} - complete - no errors")
            rc = 0
        except IOError as ioe:
            print(f"load({filename} - IOError: {ioe}")
        except Exception as e:
            print(f"load({filename} - Unexpected exception: {e}") 

        if rc == 0:
            print(f"marking conversion of {filename} complete")
        else:
            print(f"conversion {filename} failed")

        # update inventory table
        row[2] = int(time.time())
        row[3] = rc
        table[index] = row
        
    print("sleeping")
    time.sleep(sleep_time)   # sleep for a bit to avoid excess cpu 

print('unexpected exit')
