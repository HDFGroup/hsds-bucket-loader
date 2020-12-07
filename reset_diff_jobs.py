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

import sys
from datetime import datetime
import time
import h5pyd
import config

def formatTime(timestamp):
    # local_timezone = tzlocal.get_localzone() # get pytz timezone
    local_time = datetime.fromtimestamp(timestamp) # , local_timezone)
    return local_time

if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
    print("usage: python reset_failed_jobs [elapse_time]")
    print("resets any rows in the inventory file were the start time was greater than 'elapse_time' minutes (default 240m)")
    sys.exit(0)

if len(sys.argv) > 1:
    elapse_time = int(sys.argv[1])
else:
    elapse_time = 240

print("resetting diff jobs")
print("")


tgt_bucket = config.get("tgt_bucket")
username = config.get("hs_username")
password = config.get("hs_password")
endpoint = config.get("hsds_global")

inventory_domain = config.get("inventory_domain")  


f = h5pyd.File(inventory_domain, "r+", endpoint=endpoint, username=username, password=password, bucket=tgt_bucket)
table = f["inventory"]

now = time.time()
reset_count = 0

for i in range(table.nrows):
    row = table[i]
    filename = row[0].decode('utf-8')
    if row[5] > 0:
        row[5] = 0
        row[6] = 0
        row[7] = 0
        row[8] = b''
        row[9] = b''
        print(f"resetting {filename} diff")
        table[i] = row
        reset_count += 1
    
print(f"done - reset {reset_count} diff jobs")
