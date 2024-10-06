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
import re
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
    print(f"#TIME {key}:{etime}")

def untimed_run(cmd):
    print(cmd)
    rc = os.system(cmd)
    if rc!=0:
        print(f"Error: rc={rc} cmd={cmd}")
        exit(rc)

parser = argparse.ArgumentParser(description="run 2d grid checkpoint/restart testing")
parser.add_argument("--x", type=int, help="number of horizonal components", default=2)
parser.add_argument("--y", type=int, help="number of vertical components", default=1)
parser.add_argument("--clocks", type=int, help="number of clocks to run sim", default=10000)
parser.add_argument("--mpi", type=int, help="specify number of mpi threads", default=1)
parser.add_argument("--threads", type=int, help="number of sst threads per rank", default=1)
parser.add_argument("--pdf", type=bool, help="generate network graph pdf", default=False)
parser.add_argument("--period", type=int, help="time in ns between checkpoints", default=500)
parser.add_argument("--verbose", type=int, help="sst verbosity level", default=1)
args = parser.parse_args()

pfx = "restart-all_SAVE_"
if os.path.isdir(pfx):
    shutil.rmtree(pfx)

ns = args.clocks
period_ns = args.period
period = f"{period_ns}ns"
cpts_expected = int(ns/period_ns)

# bug? When using sst threads we get a checkpoint file past the end of the simulation.
if ( args.threads > 1 ):
    cpts_expected = cpts_expected + 1

cptopts = f"--checkpoint-prefix={pfx} --checkpoint-period={period}"
sstopts = f"--add-lib-path=../../sst-bench/grid"
progopts = f"--verbose={args.verbose} --x={args.x} --y={args.y} --clocks={ns}"

dotopts = ""
if args.pdf == True:
    dotopts = f"--output-dot={pfx}.dot --dot-verbosity=10"

simkey = f"{args.x}_{args.y}_{ns}_{period}"

threadopts=""
if args.threads>1:
    threadopts = f"-n {args.threads}"
    simkey = f"{simkey}_thr{args.threads}"

mpiopts=""
if args.mpi>1:
    mpiopts = f"mpirun -n {args.mpi} --use-hwthread-cpus"
    simkey = f"{simkey}_mpi{args.mpi}"


cmd=f"{mpiopts} sst  {cptopts} {sstopts} {dotopts} {threadopts} 2d.py -- {progopts}"
timed_run(cmd,f"checkpointing_{simkey}")

if args.pdf == True:
    cmd = f"dot -Tpdf {pfx}.dot -o {pfx}.pdf"
    untimed_run(cmd)

cpts=glob.glob(f"{pfx}/*/*.sstcpt")
if len(cpts) != cpts_expected:
    print(f"Error: Expected {cpts_expected} checkpoint files but found {len(cpts)}")
    exit(2)

pat=re.compile(f"(.*/.*)+/{pfx}_(.+).sstcpt$")
for cpt in cpts:
    m=pat.match(cpt)
    if m != None:
        cptkey=f"{simkey}_{m.group(m.lastindex)}"
    else:
        cptkey=f"{simkey}_?"
    cmd=f"{mpiopts} sst --load-checkpoint {cpt} {threadopts}"
    timed_run(cmd,f"restart_{cptkey}")




