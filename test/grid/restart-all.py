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
    print(cmd, flush=True)
    start = time.perf_counter()
    rc = os.system(cmd)
    etime = time.perf_counter() - start;
    if rc != 0:
        print(f"Error: rc={rc} cmd={cmd}")
        exit(rc)
    print(f"#TIME {key}:{etime}", flush=True)

def untimed_run(cmd):
    print(cmd, flush=True)
    rc = os.system(cmd)
    if rc!=0:
        print(f"Error: rc={rc} cmd={cmd}")
        exit(rc)

def cptinfo(cpt,key):
    p=os.path.dirname(cpt)
    cptSize =  sum(os.path.getsize(f"{p}/{f}") for f in os.listdir(p) if os.path.isfile(f"{p}/{f}"))
    print(f"#CPT {key}:{cptSize}", flush=True);

parser = argparse.ArgumentParser(description="run 2d grid checkpoint/restart testing")
parser.add_argument("--minDelay", type=int, help="min number of clocks between transmissions [50]", default=50)
parser.add_argument("--maxDelay", type=int, help="max number of clocks between transmissions [100]", default=100)
parser.add_argument("--clocks", type=int, help="number of clocks to run sim [1000]", default=10000)
parser.add_argument("--minData", type=int, help="Minimum number of dwords transmitted per link [10]", default=10)
parser.add_argument("--maxData", type=int, help="Maximum number of dwords transmitted per link [256]", default=256)
parser.add_argument("--nobase", type=bool, help="skip running test with no checkpointing [False]", default=False)
parser.add_argument("--numBytes", type=int, help="Internal state size (4 byte increments) [16384]", default=16384)
parser.add_argument("--pdf", type=bool, help="generate network graph pdf [False]", default=False)
parser.add_argument("--period", type=int, help="time in ns between checkpoints [1000]", default=1000)
parser.add_argument("--ranks", type=int, help="specify number of mpi ranks [1]", default=1)
parser.add_argument("--rngSeed", type=int, help="seed for random number generator [1223]", default=1223)
parser.add_argument("--threads", type=int, help="number of sst threads per rank [1]", default=1)
parser.add_argument("--verbose", type=int, help="sst verbosity level [1]", default=1)
parser.add_argument("--x", type=int, help="number of horizonal components [2]", default=2)
parser.add_argument("--y", type=int, help="number of vertical components [1]", default=1)

args = parser.parse_args()
for arg in vars(args):
    print("\t", arg, " = ", getattr(args, arg))

ns = args.clocks
period_ns = args.period
period = f"{period_ns}ns"
cpts_expected = int(ns/period_ns)

pfx = f"_cpt_x{args.x}y{args.y}r{args.ranks}t{args.threads}c{args.clocks}p{args.period}"
if os.path.isdir(pfx):
    shutil.rmtree(pfx)

cptopts = f"--checkpoint-prefix={pfx} --checkpoint-period={period}"
sstopts = f"--add-lib-path=../../sst-bench/grid"

# grid component parameters
#  verbose: Sets the verbosity level of output  [0]
#  numBytes: Internal state size (4 byte increments)  [16384]
#  numPorts: Number of external ports  [8] (must be 8 for now)
#  minData: Minimum number of unsigned values  [10]
#  maxData: Maximum number of unsigned values  [8192]
#  minDelay: Minumum clock delay between sends  [50]
#  maxDelay: Maximum clock delay between sends  [100]
#  clocks: Clock cycles to execute  [1000]
#  clockFreq: Clock frequency  [1GHz]
#  rngSeed: Mersenne RNG Seed  [1223]
           
progopts = f"--verbose={args.verbose} --x={args.x} --y={args.y} --clocks={ns} --numBytes={args.numBytes} --minData={args.minData} --maxData={args.maxData} --minDelay={args.minDelay} --maxDelay={args.maxDelay}"

dotopts = ""
if args.pdf == True:
    dotopts = f"--output-dot={pfx}.dot --dot-verbosity=10"

threadopts=""
if args.threads>1:
    threadopts = f"-n {args.threads}"

mpiopts=""
#TODO option to use hardware threads ( or not )
if args.ranks>1:
    mpiopts = f"mpirun -n {args.ranks} --use-hwthread-cpus"

if args.nobase == False:
    cmd=f"{mpiopts} sst {sstopts} {dotopts} {threadopts} 2d.py -- {progopts}"
    timed_run(cmd,f"base_{pfx}")

cmd=f"{mpiopts} sst  {cptopts} {sstopts} {dotopts} {threadopts} 2d.py -- {progopts}"
timed_run(cmd,f"checkpointing_{pfx}")

if args.pdf == True:
    cmd = f"dot -Tpdf {pfx}.dot -o {pfx}.pdf"
    untimed_run(cmd)

# bug? Sometimes using sst threads we get a checkpoint file past the end of the simulation.
cpts=glob.glob(f"{pfx}/*/*.sstcpt")
if len(cpts) != cpts_expected and len(cpts) != ( cpts_expected + 1 ):
    print(f"Error: Expected {cpts_expected} checkpoint files but found {len(cpts)}")
    exit(2)

pat=re.compile(f"(.*/.*)+/{pfx}_(.+).sstcpt$")
for cpt in cpts:
    m=pat.match(cpt)
    if m != None:
        cptkey=f"{pfx}_{m.group(m.lastindex)}"
    else:
        cptkey=f"{pfx}_?"
    cmd=f"{mpiopts} sst --load-checkpoint {cpt} {threadopts}"
    timed_run(cmd,f"restart_{cptkey}")
    cptinfo(cpt,cptkey)

#EOF




