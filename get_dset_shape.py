import sys
import s3fs
import logging


import h5py
import h5pyd 


def visit(name):
    dset = f[name]
    if isinstance(dset.id.id, str) and not dset.id.id.startswith("d-"):
        # hsds, but not a dataset
        return None
    if isinstance(dset.id.id, int) and not isinstance(dset, h5py.Dataset):
        # skip groups
        return None
     
    shape = dset.shape
    maxshape = dset.maxshape
    logging.info(f'{name} got shape: {shape}, maxshape: {maxshape}')
    dset_info = {}
    dset_info["dtype"] = dset.dtype
    dset_info["shape"] = shape
    if maxshape:
        dset_info["maxshape"] = maxshape
    if dset.chunks:
        dset_info["chunks"] = dset.chunks
    shape_map[name] = dset_info
    return None

#
# Main
#

loglevel = logging.ERROR
logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel)
shape_map = {}

if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
    print("usage: python get_dset_means.py filepath [--h5path path]")
    print("filepath can be a posix HDF5 file, a s3 uri to an hdf5 file, or an HSDS domain path")
    sys.exit(0)

filename = sys.argv[1]
if filename.startswith("s3://"):
    s3 = s3fs.S3FileSystem(use_ssl=False)
    f = h5py.File(s3.open(filename, "rb"), mode='r')
elif filename.startswith("hdf5://"):
    f = h5pyd.File(filename, mode='r', use_cache=False)
else:
    f = h5py.File(filename, mode="r")
if len(sys.argv) > 2 and sys.argv[2] == "--h5path":
    h5path = sys.argv[3]
else:
    h5path = None


if h5path:
    visit(h5path)
else:
    # traverse all datasets in file
    f.visit(visit)
names = list(shape_map.keys())
names.sort()
for name in names:
    dset_info = shape_map[name]
    print(f"{name}: {dset_info['shape']}, {dset_info['dtype']}")
    if "maxshape" in dset_info:
        print(f"   maxshape: {dset_info['maxshape']}")
    if "chunks" in dset_info:
        print(f"   chunks: {dset_info['chunks']}")
print('done!')

 




