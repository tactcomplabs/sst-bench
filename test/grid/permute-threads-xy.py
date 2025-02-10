#!/usr/bin/env python3

#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# permute-threads-xy.py
#

import argparse
import os
import sys

def untimed_run(cmd, norun):
    print("\n###########################################################################", flush=True)
    print(cmd, flush=True)
    print("###########################################################################", flush=True)
    if norun==False:
        rc = os.system(cmd)
        if rc != 0:
            print(f"Error: rc={rc} cmd={cmd}")
            sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="run 2d grid checkpoint/restart test by permuting x,y dimensions and threads")
    parser.add_argument("--maxrows", type=int, help="maximum number of vertical components [1]", default=1)
    parser.add_argument("--maxcols", type=int, help="maximum number of horizontal components [2]", default=2)
    parser.add_argument("--maxranks", type=int, help="maximum number of ranks [1]", default=1)
    parser.add_argument("--maxthreads", type=int, help="maximum number of threads [1]", default=1)
    parser.add_argument("--norun", action="store_true", help="print simulation commands but do not run")
    # These are restart-all.py arguments
    parser.add_argument("--clocks", type=int, help="number of clocks to run sim [10000]", default=10000)
    parser.add_argument("--db", type=str, help="sqlite database file [restart-all.db]", default="restart-all.db")
    # parser.add_argument("--prune", action="store_true", help="remove check checkpoint data files when done [False]")
    parser.add_argument("--minDelay", type=int, help="min number of clocks between transmissions [50]", default=50)
    parser.add_argument("--maxDelay", type=int, help="max number of clocks between transmissions [100]", default=100)
    parser.add_argument("--minData", type=int, help="Minimum number of dwords transmitted per link [10]", default=10)
    parser.add_argument("--maxData", type=int, help="Maximum number of dwords transmitted per link [256]", default=256)
    parser.add_argument("--numBytes", type=int, help="Internal state size (4 byte increments) [16384]", default=16384)
    parser.add_argument("--pdf", action="store_true", help="generate network graph pdf [False]")
    parser.add_argument("--simPeriod", type=int, help="time in ns between checkpoints. 0 disables. [0]", default=0)
    parser.add_argument("--wallPeriod", type=str, help="time %%H:%%M:%%S between checkpoints. 0 disables. [None]", default=None)
    # parser.add_argument("--ranks", type=int, help="specify number of mpi ranks [1]", default=1)
    parser.add_argument("--rngSeed", type=int, help="seed for random number generator [1223]", default=1223)
    # parser.add_argument("--threads", type=int, help="number of sst threads per rank [1]", default=1)
    parser.add_argument("--verbose", type=int, help="sst verbosity level [1]", default=1)
    # parser.add_argument("--x", type=int, help="number of horizonal components [2]", default=2)
    # parser.add_argument("--y", type=int, help="number of vertical components [1]", default=1)

    args = parser.parse_args()

    periodOpts = ""
    if args.wallPeriod != None:
        periodOpts = f"--wallPeriod={args.wallPeriod}"
    else:
        periodOpts = f"--simPeriod={args.simPeriod}"

    useRanks = args.maxranks > 1
    useThreads = args.maxthreads > 1
    if useRanks == True and useThreads == True:
        print("Currently only supporting ranks or threads, but not both")
        sys.exit(1)

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
            done = False
            for k in keys:
                if k in simlog:
                    done=True
            if done==True:
                continue;
            simlog[k] = True
            procLimit = x * y
            if procLimit > maxProcesses:
                procLimit = maxProcesses 
            for threads in range(1, procLimit+1):
                c = f"./restart-all.py --x={x} --y={y}"
                if useRanks == True or useThreads == True:
                    c = f"{c} {procOpt}{threads}"
                c = f"{c} --clocks={args.clocks} {periodOpts}"
                c = f"{c} --minDelay={args.minDelay} --maxDelay={args.maxDelay}"
                c = f"{c} --minData={args.minData} --maxData={args.maxData} --numBytes={args.numBytes}"
                c = f"{c} --rngSeed={args.rngSeed}"
                c = f"{c} --verbose={args.verbose}  --db={args.db} --prune"
                untimed_run(c, args.norun)
                numSims = numSims + 1

    print(f"Number of Simulations {numSims}")
    print("permute-threads-xy.py comleted normally")

#EOF
