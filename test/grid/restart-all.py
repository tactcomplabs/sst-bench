#!/usr/bin/env python3 

#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# restart-all.py
#

import argparse
import glob
import os
import shutil
import time

def timed_run(cmd, key):
    print(cmd)
    start = time.perf_counter()
    rc = os.system(cmd)
    etime = time.perf_counter() - start;
    if rc!=0:
        print(f"Error: rc={rc} cmd={cmd}")
        exit(rc)
    print(f"TIME {key}:{etime}")

def untimed_run(cmd):
    print(cmd)
    rc = os.system(cmd)
    if rc!=0:
        print(f"Error: rc={rc} cmd={cmd}")
        exit(rc)

parser = argparse.ArgumentParser(description="run 2d grid checkpoint/restart testing")
parser.add_argument("--x", type=int, help="number of horizonal components", default=2)
parser.add_argument("--y", type=int, help="number of vertical components", default=1)
parser.add_argument("--mpi", type=int, help="specify number of mpi threads", default=1)
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
progopts=f"--verbose={args.verbose} --x={args.x} --y={args.y}"

dotopts=""
if args.pdf==True:
    dotopts=f"--output-dot={pfx}.dot --dot-verbosity=10"

simkey = f"{period}_{args.x}_{args.y}"

mpiopts=""
if args.mpi>1:
    mpiopts=f"mpirun -n {args.mpi} --use-hwthread-cpus"
    sstopts=f"{sstopts} --parallel-output=1"
    simkey = f"{simkey}_{args.mpi}"

cmd=f"{mpiopts} sst  {cptopts} {sstopts} {dotopts} 2d.py -- {progopts}"
timed_run(cmd,f"checkpointing_{simkey}")

if args.pdf == True:
    cmd = f"dot -Tpdf {pfx}.dot -o {pfx}.pdf"
    untimed_run(cmd)

cpts=glob.glob(f"{pfx}/*/*.sstcpt")
if len(cpts) != cpts_expected:
    print(f"Error: Expected {cpts_expected} checkpoint files but found {len(cpts)}")
    exit(2)

for cpt in cpts:
    cmd=f"{mpiopts} sst --load-checkpoint {cpt} {sstopts}"
    timed_run(cmd,f"restart_{simkey}")




