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
import time
import boto3
import h5pyd
import config

src_bucket = config.get("src_bucket")
src_prefix = config.get("src_prefix")
src_suffix = config.get("src_suffix")

tgt_bucket = config.get("tgt_bucket")
username = config.get("hs_username")
password = config.get("hs_password")
endpoint = config.get("hsds_global")

inventory_domain = config.get("inventory_domain")
sleep_time = config.get("watchdog_sleep_time")

s3_paginator = boto3.client('s3').get_paginator('list_objects_v2')

def keys(bucket_name, prefix='/', delimiter='/', start_after=''):
    prefix = prefix[1:] if prefix.startswith(delimiter) else prefix
    start_after = (start_after or prefix) if prefix.endswith(delimiter) else start_after
    for page in s3_paginator.paginate(Bucket=bucket_name, Prefix=prefix, StartAfter=start_after):
        for content in page.get('Contents', ()):
            yield content['Key']
            

def watch_bucket():
    print(f"watching bucket: {src_bucket}, prefix: {src_prefix}")
    f = h5pyd.File(inventory_domain, "r+", endpoint=endpoint, username=username, password=password, bucket=tgt_bucket)
    table = f["inventory"]
    for key in keys(src_bucket, prefix=src_prefix):
        if src_suffix and not key.endswith(src_suffix):
            continue
        condition = f"filename == b'{key}'"
        matches = table.read_where(condition, limit=1)
        if len(matches) == 0:
            print(f"not found, adding filename: {key}")
            row = (key, 0, 0, 0, "")
            table.append([row,])
        else:
            pass  # filename found
    f.close()

#
# main
#

print("watchdog starting")

while True:
    watch_bucket()
    print(f"sleeping for {sleep_time} seconds")
    time.sleep(sleep_time)  # sleep for a bit
