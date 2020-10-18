import sys
from datetime import datetime
import tzlocal
import h5pyd
import config

def formatTime(timestamp):
    local_timezone = tzlocal.get_localzone() # get pytz timezone
    local_time = datetime.fromtimestamp(timestamp, local_timezone)
    return local_time

tgt_bucket = config.get("tgt_bucket")
username = config.get("hs_username")
password = config.get("hs_password")
endpoint = config.get("hsds_global")

inventory_domain = config.get("inventory_domain")  

f = h5pyd.File(inventory_domain, "r", endpoint=endpoint, username=username, password=password, bucket=tgt_bucket)
print(f"{inventory_domain} found, owner: {f.owner}, last madified: {formatTime(f.modified)}")
print("Contents")
print("\tFilename\tStart\tDone")
print("-"*80)
table = f["inventory"]
for row in table:
    filename = row[0].decode('utf-8')
    if row[1]:
        start = formatTime(row[1])
    else:
        start = 0
    if row[2]:
        stop = formatTime(row[2])
    else:
        stop = 0
    print(f"\t{filename}\t{start}\t{stop}")
print(f"{table.nrows} rows")
