#!/usr/bin/env python3 

import glob
import os
import shutil

pfx = "restart-all_SAVE_"
if os.path.isdir(pfx):
    shutil.rmtree(pfx)

ns=10000
period_ns=500
period=f"{period_ns}ns"
cpts_expected=ns/period_ns

cmd=f"sst --checkpoint-prefix={pfx} --checkpoint-period={period} --add-lib-path=../../sst-bench/grid 2d.py -- --verbose=0"
print(cmd)
rc = os.system(cmd)
if rc!=0:
    print(f"Error: sst checkpointing test failed. rc={rc}")
    exit(1)

cpts=glob.glob(f"{pfx}/*/*.sstcpt")
if len(cpts) != cpts_expected:
    print(f"Error: Expected {cpts_expected} checkpoint files but found {len(cpts)}")
    exit(2)

for cpt in cpts:
    cmd=f"sst --add-lib-path=../../sst-bench/grid --load-checkpoint {cpt}"
    print(cmd)
    rc = os.system(cmd)
    if rc!=0:
        print(f"Error: sst restart test failed for checkpoint {cpt}. rc={rc}")
        exit(3)




