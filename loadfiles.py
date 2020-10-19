import time
import os
import logging
import subprocess
import h5pyd
import config

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


def load_file(filename):
    print(f"load_file: {filename}")
    print(f"got filename: {filename} from {inventory_domain}")
    # got filename: data/hdf5test/snp500.h5 from /home/john/bucketloader/inventory.h5
    s3path = f"s3://{src_bucket}{src_prefix}{filename}"
    print(f"using s3path: {s3path}")
    tgt_path = tgt_folder + filename
    print(f"tgt_path: {tgt_path}")
    ensure_folder(os.path.dirname(tgt_path))  # tbd ignore 409 errors?
    # using s3path: s3://hdf5.sample/data/hdf5test/snp500.h5
    # run hsload on the s3 uri

    # make sure the local hsds is up (if being used)
    if hsds_local:
        endpoint = hsds_local
    else:
        endpoint = hsds_global
    hsload_args = ["hsload",]
    hsload_args.append("--endpoint")
    hsload_args.append(endpoint)
    if username:
        hsload_args.append("--username")
        hsload_args.append(username)
    if password:
        hsload_args.append("--password")
        hsload_args.append(password)
    if tgt_bucket:
        hsload_args.append("--bucket")
        hsload_args.append(tgt_bucket)
    if link_files:
        hsload_args.append("--link")
    hsload_args.append(s3path)
    hsload_args.append(tgt_path)
    print(f"running hsload {s3path} {tgt_path}")
    rc = subprocess.run(hsload_args)
    if rc.returncode > 0:
        logging.error(f"load_file error for {filename}")
        return False

    if config.get("public_read"):
        # make public read, and get acl
        print("adding public read ACL")
        f = h5pyd.File(tgt_path, "r+", endpoint=endpoint, username=username, password=password, bucket=tgt_bucket)
        acl = {"userName": "default"}
        acl["create"] = False
        acl["read"] = True
        acl["update"] = False
        acl["delete"] = False
        acl["readACL"] = True
        acl["updateACL"] = False
        f.putACL(acl)
        f.close()

    if rc.returncode == 0:
        return True
    else:
        return False

### main

loglevel = logging.ERROR
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
for i in range(table.nrows):
    row = table[i]
    print(f"row[{i}]: {row}")

condition = "start == 0"  # query for files that haven't been proccessed

while True:
    now = int(time.time())
    update_val = {"start": now}
    # query for row with 0 start value and update it to now
    indices = table.update_where(condition, update_val, limit=1)
    print("indices:", indices)

    if indices is not None and len(indices) > 0:
        index = indices[0]
        print(f"getting row: {index}")
        row = table[index]
        print("got row:", row)
        filename = row[0].decode("utf-8")
        if load_file(filename):
            print(f"marking conversion of {filename} complete")
            row[2] = int(time.time())
            table[index] = row
        else:
            print(f"load_file {filename} failed")

    else:
        # no available rows
        print("sleeping")
        time.sleep(sleep_time)   # sleep for a bit to avoid endless restarts
logging.error("Unexpected exit")
print('exit')
