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
print("\tFilename\t\tStart\t\t\tDone\trc\tpod")
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
    rc = row[3]
    podname = row[4].decode('utf-8')
    print(f"\t{filename}\t{start}\t{stop}\t{rc}\t{podname}")
print(f"{table.nrows} rows")
