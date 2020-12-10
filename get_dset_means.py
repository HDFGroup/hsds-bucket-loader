import sys
import logging

USE_H5PY=0
if USE_H5PY:
    import h5py
else:
    import h5pyd as h5py


from chunkiter import ChunkIterator

def get_mean(dset):
    means = []
    try:
        it = ChunkIterator(dset)

        for s in it:
            msg = "checking dataset data for slice: {}".format(s)
            logging.debug(msg)

            arr = dset[s]
            msg = "got array {}".format(arr.shape)
            logging.debug(msg)
            means.append(arr.mean())
    
    except (IOError, TypeError) as e:
        msg = "ERROR : failed to copy dataset data : {}".format(str(e))
        logging.error(msg)
        print(msg)
    sum = 0.0
    for f in means:
        sum += f
    if len(means) > 0:
        mean = sum / float(len(means)) 
    return mean



def visit(name):
    dset = f[name]
    if not isinstance(dset, h5py.Dataset):
        # skip groups
        return None
    if dset.dtype.kind != 'f':
        # skip non-floats
        return None
   
    mean = get_mean(dset)
    logging.info(f'{name} got mean: {mean}')
    mean_map[name] = mean
    return None

#
# Main
#

loglevel = logging.ERROR
logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel)
mean_map = {}

if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
    print("usage: python get_dset_means.py <domain>")
    sys.exit(0)

domain = sys.argv[1]

f = h5py.File(domain, mode="r")
f.visit(visit)

names = list(mean_map.keys())
names.sort()
for name in names:
    mean = mean_map[name]
    print(f"{name}: {mean:.2f}")

 




