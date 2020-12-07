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
import h5pyd
import config

tgt_bucket = config.get("tgt_bucket")
username = config.get("hs_username")
password = config.get("hs_password")
endpoint = config.get("hsds_global")
 
inventory_domain = config.get("inventory_domain")
print("creating inventory domain:", inventory_domain)
if tgt_bucket:
    print("tgt_bucket:", tgt_bucket)
f = h5pyd.File(inventory_domain, "x", endpoint=endpoint, username=username, password=password, bucket=tgt_bucket)
dt=[("filename", "S64"), ("loadstart", "i8"), ("loaddone", "i8"), ('loadstatus', "i4"), ('loadpodname', "S40"),
                          ("diffstart", "i8"), ("diffdone", "i8"), ('diffstatus', "i4"), ('diffpodname', "S40")]
table = f.create_table("inventory", dtype=dt)

if config.get("public_read"):
    # make public read, and get acl
    acl = {"userName": "default"}
    acl["create"] = False
    acl["read"] = True
    acl["update"] = False
    acl["delete"] = False
    acl["readACL"] = True
    acl["updateACL"] = False
    f.putACL(acl)
    f.close()

print(f"created inventory: {inventory_domain}")
