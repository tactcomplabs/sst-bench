#!/usr/bin/env python3

#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# parallel-permute.py
#

import argparse
import os

def untimed_run(cmd, norun):
    print("\n###########################################################################", flush=True)
    print(cmd, flush=True)
    print("###########################################################################", flush=True)
    if norun==False:
        rc = os.system(cmd)
        if rc != 0:
            print(f"Error: rc={rc} cmd={cmd}")
            exit(rc)

parser = argparse.ArgumentParser(description="run 2d grid checkpoint/restart testing")
parser.add_argument("--maxrows", type=int, help="maximum number of vertical components", default=1)
parser.add_argument("--maxcols", type=int, help="maximum number of horizontal components", default=2)
parser.add_argument("--maxranks", type=int, help="maximum number of ranks", default=1)
parser.add_argument("--maxthreads", type=int, help="maximum number of threads", default=1)
parser.add_argument("--norun", type=bool, help="print simulation commands but do not run", default=False)
# These are restart-all.py arguments
# TODO permute clocks and period as well
parser.add_argument("--clocks", type=int, help="number of clocks to run sim", default=10000)
parser.add_argument("--period", type=int, help="time in ns between checkpoints", default=1000)
# parser.add_argument("--pdf", type=bool, help="generate network graph pdf", default=False)
parser.add_argument("--verbose", type=int, help="sst verbosity level", default=1)
args = parser.parse_args()

useRanks = args.maxranks > 1
useThreads = args.maxthreads > 1
if useRanks == True and useThreads == True:
    print("Currently only supporting ranks or threads, but not both")
    exit(1)

maxProcesses = args.maxranks
procOpt = ""
if useRanks:
    maxProcesses = args.maxranks
    procOpt = f"--ranks="
elif useThreads:
    maxProcesses = args.maxthreads
    procOpt = f"--threads="

# Assume symmetry to cut number of sims in half
# We can store more interesting data in this dictionary
simlog = {"1_1" : True }
numSims = 0
for x in range(1, args.maxcols+1):
    for y in range(1, args.maxrows+1):
        keys = [ f"{x}_{y}", f"{y}_{x}" ]
        for k in keys:
            if k in simlog:
                continue
            simlog[k] = True
        procLimit = x * y
        if procLimit > maxProcesses:
            procLimit = maxProcesses 
        for threads in range(1, procLimit+1):
            c = f"./restart-all.py --x={x} --y={y}"
            if useRanks == True or useThreads == True:
                c = f"{c} {procOpt}{threads}"
            c = f"{c} --clocks={args.clocks} --period={args.period}"
            c = f"{c} --verbose={args.verbose}"
            untimed_run(c, args.norun)
            numSims = numSims + 1

print(f"Number of Simulations {numSims}")

#EOF
