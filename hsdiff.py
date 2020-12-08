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

import logging
import numpy as np

if __name__ == "hsdiff":
    from chunkiter import ChunkIterator
else:
    from .chunkiter import ChunkIterator

def record_diff(ctx, msg):
    if ctx["verbose"]:
        print(msg)
    logging.info(msg)
    ctx["differences"] += 1
    if not ctx["diff_msg"]:
        # save description of first diff
        ctx["diff_msg"] = msg


def diff_attrs(src, tgt, ctx):
    """ compare attributes of src and tgt """
    msg = "checking attributes of {}".format(src.name)
    logging.debug(msg)

    if len(src.attrs) != len(tgt.attrs):
        msg = "<{}> have a different number of attribute from <{}>".format(src.name, tgt.name)
        record_diff(ctx, msg)
        return False

    for name in src.attrs:
        msg = "checking attribute {} of {}".format(name, src.name)
        logging.debug(msg)
        if ctx["verbose"]:
            print(msg)
        if name not in tgt.attrs:
            msg = "<{}>  has attribute {} not found in <{}>".format(src.name, name, tgt.name)
            record_diff(ctx, msg)
            return False
        src_attr = src.attrs[name]
        tgt_attr = tgt.attrs[name]
        if isinstance(src_attr, np.ndarray):
            # compare shape, type, and values
            if src_attr.dtype != tgt_attr.dtype:
                msg = "Type of attribute {} of <{}> is different".format(name, src.name)
                record_diff(ctx, msg)
                return False
            if src_attr.shape != tgt_attr.shape:
                msg = "Shape of attribute {} of <{}> is different".format(name, src.name)
                record_diff(ctx, msg)
                return False
            if hash(src_attr.tostring()) != hash(tgt_attr.tostring()):
                msg = "values for attribute {} of <{}> differ".format(name, src.name)
                record_diff(ctx, msg)
                return False
        elif src_attr != tgt_attr:
            # returned as int or string, just compare values
            msg = "<{}>  has attribute {} different than <{}>".format(src.name, name, tgt.name)
            record_diff(ctx, msg)
            return False

    # of of attribute iteration
    return True


def diff_group(src, ctx):
    """ compare group in src and tgt
    """
    msg = "checking group <{}>".format(src.name)
    logging.info(msg)
    if ctx["verbose"]:
        print(msg)

    fout = ctx["fout"]

    if src.name not in fout:
        msg = "<{}> not found in target".format(src.name)
        record_diff(ctx, msg)
        return False

    tgt = fout[src.name]

    # printed when there is a difference
    if len(src) != len(tgt):
        msg = "{} group have a different number of links from {}".format(src.name, tgt.name)
        record_diff(ctx, msg)
        return False

    for title in src:
        if ctx["verbose"]:
            print("got link: '{}' of group <{}>".format(title, src.name))
        if title not in tgt:
            msg = "<{}> group has link {} not found in <{}>".format(src.name, title, tgt.name)
            record_diff(ctx, msg)
            return False

        lnk_src = src.get(title, getlink=True)
        lnk_src_type = lnk_src.__class__.__name__
        lnk_tgt = tgt.get(title, getlink=True)
        lnk_tgt_type = lnk_tgt.__class__.__name__
        if lnk_src_type != lnk_tgt_type:
            msg = "<{}> group has link {} of different type than found in <{}>".format(src.name, title, tgt.name)
            record_diff(ctx, msg)
            return False

        if lnk_src_type == "HardLink":
            logging.debug("Got hardlink: {}".format(title))
            # TBD: handle the case where multiple hardlinks point to same object
        elif lnk_src_type == "SoftLink":
            msg = "Got SoftLink({}) with title: {}".format(lnk_src.path, title)
            if ctx["verbose"]:
                print(msg)
            logging.info(msg)
            if lnk_src.path != lnk_tgt.path:
                msg = "<{}> group has link {} with different path than <{}>".format(src.name, title, tgt.name)
                record_diff(ctx, msg)
                return False
        elif lnk_src_type == "ExternalLink":
            msg = "<{}> group has ExternalLink {} ({}, {})".format(src.name, title, lnk_src.filename, lnk_src.path)
            if ctx["verbose"]:
                print(msg)
            logging.info(msg)
            if lnk_src.filename != lnk_tgt.filename:
                msg = "<{}> group has external link {} with different filename than <{}>".format(src.name, title, tgt.name)
                record_diff(ctx, msg)
                return False
            if lnk_src.path != lnk_tgt.path:
                msg = "<{}> group has external link {} with different path than <{}>".format(src.name, title, tgt.name)
                record_diff(ctx, msg)
                return False
        else:
            msg = "Unexpected link type: {}".format(lnk_src_type)
            logging.warning(msg)
            if ctx["verbose"]:
                print(msg)
    # end link iteration

    if not ctx["noattr"]:
        result = diff_attrs(src, tgt, ctx)
    else:
        result = True
    return result



def diff_datatype(src, ctx):
    """ compare datatype objects in src and tgt
    """
    msg = "checking datatype <{}>".format(src.name)
    logging.info(msg)
    if ctx["verbose"]:
        print(msg)

    fout = ctx["fout"]

    if src.name not in fout:
        msg = "<{}> not found in target".format(src.name)
        record_diff(ctx, msg)
        return False
    tgt = fout[src.name]

    if tgt.dtype != src.dtype:
        msg = "Type of <{}> is different".format(src.name)
        record_diff(ctx, msg)
        return False

    if not ctx["noattr"]:
        result = diff_attrs(src, tgt, ctx)
    else:
        result = True
    return result


def diff_dataset(src, ctx):
    """ compare dataset in src and tgt
    """
    msg = "checking dataset <{}>".format(src.name)
    logging.info(msg)
    if ctx["verbose"]:
        print(msg)

    fout = ctx["fout"]

    if src.name not in fout:
        msg = "<{}> not found in target".format(src.name)
        record_diff(ctx, msg)
        return False
    tgt = fout[src.name]

    try:
        tgt_shape = tgt.shape
    except AttributeError:
        msg = "<{}> in target not a dataset".format(src.name)
        logging.info(msg)
        record_diff(ctx, msg)
        return False

    # printed when there is a difference
    if tgt_shape != src.shape:
        msg = "Shape of <{}> is different".format(src.name)
        record_diff(ctx, msg)

        return False

    if tgt.dtype != src.dtype:
        msg = "Type of <{}> is different".format(src.name)
        record_diff(ctx, msg)
        return False

    # TBD - check fillvalue

    if ctx["nodata"]:
        # skip data compare
        return True

    try:
        it = ChunkIterator(src)

        for s in it:
            msg = "checking dataset data for slice: {}".format(s)
            logging.debug(msg)

            arr_src = src[s]
            msg = "got src array {}".format(arr_src.shape)
            logging.debug(msg)
            arr_tgt = tgt[s]
            msg = "got tgt array {}".format(arr_tgt.shape)
            logging.debug(msg)

            if hash(arr_src.tostring()) != hash(arr_tgt.tostring()):
                msg = "values for dataset {} differ for slice: {}".format(src.name, s)
                record_diff(ctx, msg)
                return False

    except (IOError, TypeError) as e:
        msg = "ERROR : failed to copy dataset data : {}".format(str(e))
        logging.error(msg)
        print(msg)

    if not ctx["noattr"]:
        result = diff_attrs(src, tgt, ctx)
    else:
        result = True
    return result



def diff_file(fin, fout, verbose=False, nodata=False, noattr=False, quiet=False):
    ctx = {}
    ctx["fin"] = fin
    ctx["fout"] = fout
    ctx["verbose"] = verbose
    ctx["nodata"] = nodata
    ctx["noattr"] = noattr
    ctx["quiet"] = quiet
    ctx["differences"] = 0
    ctx["diff_msg"] = ""


    def object_diff_helper(name, obj):
        class_name = obj.__class__.__name__

        if class_name in ("Dataset", "Table"):
            diff_dataset(obj, ctx)
        elif class_name == "Group":
            diff_group(obj, ctx)
        elif class_name == "Datatype":
            diff_datatype(obj, ctx)
        else:
            logging.error("no handler for object class: {}".format(type(obj)))

    # check links in root group
    diff_group(fin, ctx)

    # build a rough map of the file using the internal function above
    fin.visititems(object_diff_helper)
    differences = ctx["differences"]
    result = None
    if  differences> 0:
        logging.info(f"found {differences} differences")
        if ctx["diff_msg"]:
            result = ctx["diff_msg"]
        else:
            result = "files differ"
    else:
        logging.info("no differences")

    return result

 
