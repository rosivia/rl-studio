import numpy as np, glob, os, sys
src, out = sys.argv[1], sys.argv[2]
v = {os.path.basename(f)[:-4]: np.fromfile(f, dtype=np.float32).reshape(-1,1,256) for f in glob.glob(src+'/*.bin')}
np.savez(out, **v); print(len(v), 'voices', next(iter(v.values())).shape)
