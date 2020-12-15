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
    shape_map[name] = (shape, maxshape)
    return None

#
# Main
#

loglevel = logging.ERROR
logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel)
shape_map = {}

if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
    print("usage: python get_dset_means.py <domain>")
    sys.exit(0)

filename = sys.argv[1]
if filename.startswith("s3://"):
    s3 = s3fs.S3FileSystem(use_ssl=False)
    f = h5py.File(s3.open(filename, "rb"), mode='r')
elif filename.startswith("hdf5://"):
    f = h5pyd.File(filename, mode='r', use_cache=False)
else:
    f = h5py.File(filename, mode="r")
f.visit(visit)
names = list(shape_map.keys())
names.sort()
for name in names:
    (shape, maxshape) = shape_map[name]
    if shape == maxshape:
        print(f"{name}: {shape}")
    else:
        print(f"{name}: {shape}, {maxshape}")
print('done!')

 




