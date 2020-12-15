import sys
import s3fs
import logging

USE_H5PY=1
if USE_H5PY:
    import h5py
else:
    import h5pyd as h5py


def visit(name):
    dset = f[name]
    if not isinstance(dset, h5py.Dataset):
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

loglevel = logging.INFO
logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel)
shape_map = {}

if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
    print("usage: python get_dset_means.py <domain>")
    sys.exit(0)

filename = sys.argv[1]
if filename.startswith("s3://"):
    s3 = s3fs.S3FileSystem(use_ssl=False)
    f = h5py.File(s3.open(filename, "rb"), mode='r')
else:
    f = h5py.File(filename, mode="r", use_cache=False)
f.visit(visit)
names = list(shape_map.keys())
names.sort()
for name in names:
    (shape, maxshape) = shape_map[name]
    if shape == maxshape:
        print(f"{name}: {shape}")
    else:
        print(f"{name}: {shape}, {maxshape}")

 




