##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of HSDS (HDF5 Scalable Data Service), Libraries and      #
# Utilities.  The full HSDS copyright notice, including                      #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################

from datetime import datetime
import h5pyd
import config

def formatTime(timestamp):
    # local_timezone = tzlocal.get_localzone() # get pytz timezone
    local_time = datetime.fromtimestamp(timestamp) # , local_timezone)
    return local_time

tgt_bucket = config.get("tgt_bucket")
username = config.get("hs_username")
password = config.get("hs_password")
endpoint = config.get("hsds_global")

inventory_domain = config.get("inventory_domain")  

f = h5pyd.File(inventory_domain, "r", endpoint=endpoint, username=username, password=password, bucket=tgt_bucket)
print(f"{inventory_domain} found, owner: {f.owner}, last madified: {datetime.fromtimestamp(f.modified)}")
print("Contents")
print("\tfilename")
print("\tload\tStart\tDone\tRuntime\trc\tPod")
print("\tDiff\tStart\tDone\tRuntime\trc\tPod\tresult")
print("-"*160)
table = f["inventory"]
for row in table:
    filename = row[0].decode('utf-8')
    if row[1]:
        load_start = formatTime(row[1])
    else:
        load_start = 0
    if row[2]:
        load_stop = formatTime(row[2])
    else:
        load_stop = 0
    load_rc = row[3]
    load_podname = row[4].decode('utf-8')
    if row[2] > 0:
        load_runtime = f"{int(row[2] - row[1]) // 60:4d}m {(row[2] - row[1]) % 60:2}s"
    else:
        load_runtime = "0"
    if row[5]:
        diff_start = formatTime(row[5])
    else:
        diff_start = 0
    if row[6]:
        diff_stop = formatTime(row[6])
    else:
        diff_stop = 0
    diff_rc = row[7]
    load_podname = row[8].decode('utf-8')
    if row[6] > 0:
        diff_runtime = f"{int(row[6] - row[5]) // 60:4d}m {(row[6] - row[5]) % 60:2}s"
    else:
        diff_runtime = "0"
    diff_podname = row[8].decode('utf-8')
    diff_result = row[9].decode('utf-8')

    print(f"{filename}")
    fmt_str = f"\tload\t{load_start}\t{load_stop}\t{load_runtime}\t{load_rc}\t{load_podname}"
    print(fmt_str)
    fmt_str = f"\tdiff\t{diff_start}\t{diff_stop}\t{diff_runtime}\t{diff_rc}\t{diff_podname}\t{diff_result}"
    print(fmt_str)
print(f"{table.nrows} rows")
