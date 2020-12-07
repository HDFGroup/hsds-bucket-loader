import time
import os
import logging
import s3fs
import h5py
import h5pyd
import config
from hsdiff import diff_file

src_bucket = config.get("src_bucket")
src_prefix = config.get("src_prefix")
src_suffix = config.get("src_suffix")
tgt_folder = config.get("tgt_folder")
tgt_bucket = config.get("tgt_bucket")
hsds_local = config.get("hsds_local")
print("hsds_local:", hsds_local)
hsds_global = config.get("hsds_global")
print("hsds_global:", hsds_global)
username = config.get("hs_username")
password = config.get("hs_password")
inventory_domain = config.get("inventory_domain")
print("inventory_domain:", inventory_domain)
sleep_time = config.get("watchdog_sleep_time")
if "POD_NAME" in os.environ:
    pod_name = os.environ["POD_NAME"]
else:
    pod_name = ""


def diff(filename):
    verbose = True
    print(f"got filename: {filename} from {inventory_domain}")
    
    # got filename: data/hdf5test/snp500.h5 from /home/john/bucketloader/inventory.h5
    s3path = f"s3://{src_bucket}/{filename}"
    print(f"using s3path: {s3path}")
    tgt_path = tgt_folder + filename
    print(f"tgt_path: {tgt_path}")

    # make sure the local hsds is up (if being used)
    if hsds_local:
        endpoint = hsds_local
    else:
        endpoint = hsds_global

    print("running diff {} and {}".format(s3path, tgt_path))
    s3 = s3fs.S3FileSystem()

    try:
        fin = h5py.File(s3.open(s3path, "rb"), "r")
    except IOError as ioe:
        logging.error("Error opening s3path {}: {}".format(s3path, ioe))
        raise

    # open domain
    try:
        fout = h5pyd.File(tgt_path, 'r', endpoint=endpoint, username=username, password=password, bucket=tgt_bucket)
    except IOError as ioe:
        if ioe.errno == 404:
            logging.error("Domain: {} not found".format(tgt_path))
        elif ioe.errno == 403:
            logging.error("No write access to domain: {}".format(tgt_path))
        else:
            logging.error("Error creating file {}: {}".format(tgt_path, ioe))
        raise

    # do the actual diff
    result = None
    try:
        result = diff_file(fin, fout, verbose=verbose)
    except IOError as ioe:
        logging.error("load_file error: {}".format(ioe))
        raise
        

    return result

### main

loglevel = config.get("log_level")
logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel)

# make sure the local hsds is up (if being used)
if hsds_local:
    state = None
    while state != "READY":
        print("waiting on local hsds READY")
        time.sleep(1)
        info = h5pyd.getServerInfo(endpoint=hsds_local)
        if info and 'state' in info:
            state = info['state']
    print("local hsds in in READY state")


f = h5pyd.File(inventory_domain, "r+", use_cache=False, endpoint=hsds_global, username=username, password=password)

table = f["inventory"]
print("table.nrows:", table.nrows)

condition = "(loaddone > 0) & (loadstatus == 0) & (diffstart == 0)"  # query for files that haven't been proccessed

while True:

    now = int(time.time())
    update_val = {"diffstart": now, "diffstatus": -1, "diffpodname": pod_name}


    # query for row with 0 start value and update it to now
    indices = table.update_where(condition, update_val, limit=1)
    print("indices:", indices)

    if indices is not None and len(indices) > 0:
        index = indices[0]
        print(f"getting row: {index}")
        row = table[index]
        print("got row:", row)
        filename = row[0].decode("utf-8")
        print(f"running diff on {filename}")
        result = ""
        try:
            result = diff(filename)
            print(f"diff({filename} - complete")
        except IOError as ioe:
            print(f"load({filename} - IOError: {ioe}")
            rc = 1
        except Exception as e:
            print(f"load({filename} - Unexpected exception: {e}") 
            rc = 1

        if result:
            print(f"diff of {filename} found differences: {result}")
            if len(result) > 80: 
                result = result[:80]
        else:
            print(f"diff check on {filename} found no diffs")

        # update inventory table
        print("current row:", row)
        row[6] = int(time.time())
        row[7] = rc
        row[9] = result
        print("updated row:", row)
        table[index] = row
        
    print(f"sleeping  {sleep_time} seconds")
    time.sleep(sleep_time)   # sleep for a bit to avoid excess cpu 

print('unexpected exit')
