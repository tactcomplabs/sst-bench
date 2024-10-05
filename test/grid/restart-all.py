#!/usr/bin/env python3 

import argparse
import glob
import os
import shutil

parser = argparse.ArgumentParser(description="run 2d grid checkpoint/restart testing")
parser.add_argument("--x", type=int, help="number of horizonal components", default=2)
parser.add_argument("--y", type=int, help="number of vertical components", default=1)
parser.add_argument("--pdf", type=bool, help="generate network graph pdf", default=False)
parser.add_argument("--period", type=int, help="time in ns between checkpoints", default=500)
parser.add_argument("--verbose", type=int, help="sst verbosity level", default=1)
args = parser.parse_args()

pfx = "restart-all_SAVE_"
if os.path.isdir(pfx):
    shutil.rmtree(pfx)

ns=10000
period_ns=args.period
period=f"{period_ns}ns"
cpts_expected=ns/period_ns

cptopts=f"--checkpoint-prefix={pfx} --checkpoint-period={period}"
sstopts=f"--add-lib-path=../../sst-bench/grid"
dotopts=f"--output-dot={pfx}.dot --dot-verbosity=10"
progopts=f"--verbose={args.verbose} --x={args.x} --y={args.y}"

cmd=f"sst  {cptopts} {sstopts} {dotopts} 2d.py -- {progopts}"
print(cmd)
rc = os.system(cmd)

if rc!=0:
    print(f"Error: sst checkpointing test failed. rc={rc}")
    exit(1)

if args.pdf == True:
    cmd = f"dot -Tpdf {pfx}.dot -o {pfx}.pdf"
    rc = os.system(cmd)

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




