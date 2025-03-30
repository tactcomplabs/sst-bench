#!/usr/bin/env python3

#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# permute-cptsize-xy.py
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
    print(' '.join(sys.argv))
    parser = argparse.ArgumentParser(
        prog='permute-cptsize.py',
        description="run 2d grid checkpoint/restart testing, restart-all.py, sweeping component size",
        epilog='Results will be appended to to sqlite3 database file, restart.db')
    parser.add_argument("--minBytes", type=int, help="minimum component size [1024]", default=1024)
    parser.add_argument("--maxBytes", type=int, help="maximum component size [65536]", default=65536)
    parser.add_argument("--steps", type=int, help="number of runs sweeping data size from 1024 to maxBytes [4]", default=4)
    parser.add_argument("--norun", action="store_true", help="print simulation commands but do not run")
    # These are restart-all.py arguments
    parser.add_argument("--clocks", type=int, help="number of clocks to run sim [10000]", default=10000)
    parser.add_argument("--db", type=str, help="sqlite database file [restart-all.db]", default="restart-all.db")
    # parser.add_argument("--prune", action="store_true", help="remove check checkpoint data files when done [False]")
    parser.add_argument("--minDelay", type=int, help="min number of clocks between transmissions [50]", default=50)
    parser.add_argument("--maxDelay", type=int, help="max number of clocks between transmissions [100]", default=100)
    parser.add_argument("--minData", type=int, help="Minimum number of dwords transmitted per link [10]", default=10)
    parser.add_argument("--maxData", type=int, help="Maximum number of dwords transmitted per link [256]", default=256)
    # parser.add_argument("--numBytes", type=int, help="Internal state size (4 byte increments) [16384]", default=16384)
    parser.add_argument("--pdf", action="store_true", help="generate network graph pdf [False]")
    parser.add_argument("--schema", action="store_true", help="generate checkpoint schema (requires sst-core/schema branch) [False]")
    parser.add_argument("--simPeriod", type=int, help="time in ns between checkpoints. 0 disables. [0]", default=0)
    parser.add_argument("--wallPeriod", type=str, help="time %%H:%%M:%%S between checkpoints. 0 disables. [None]", default=None)
    parser.add_argument("--ranks", type=int, help="specify number of mpi ranks [1]", default=1)
    parser.add_argument("--rngSeed", type=int, help="seed for random number generator [1223]", default=1223)
    parser.add_argument("--threads", type=int, help="number of sst threads per rank [1]", default=1)
    parser.add_argument("--verbose", type=int, help="sst verbosity level [1]", default=1)
    parser.add_argument("--x", type=int, help="number of horizonal components [2]", default=2)
    parser.add_argument("--y", type=int, help="number of vertical components [1]", default=1)

    args = parser.parse_args()
    
    periodOpts = ""
    if args.wallPeriod != None:
        periodOpts = f"--wallPeriod={args.wallPeriod}"
    else:
        periodOpts = f"--simPeriod={args.simPeriod}"

    schema = ""
    if args.schema == True:
        schema = "--schema"

    if args.maxBytes < args.minBytes:
        print(f"maxBytes {args.maxBytes} must be greater than minBytes {args.minBytes}")
        sys.exit(1)

    stepSize = int((args.maxBytes-args.minBytes)/args.steps)
    if stepSize == 0:
        stepSize = 1;

    numSims = 0
    for bytes in range(args.minBytes, args.maxBytes, stepSize):
        c = f"./restart-all.py --x={args.x} --y={args.y}"
        c = f"{c} --threads={args.threads} --ranks={args.ranks}"
        c = f"{c} {schema}"
        c = f"{c} --clocks={args.clocks} {periodOpts}"
        c = f"{c} --minDelay={args.minDelay} --maxDelay={args.maxDelay}"
        c = f"{c} --minData={args.minData} --maxData={args.maxData} --numBytes={bytes}"
        c = f"{c} --rngSeed={args.rngSeed}"
        c = f"{c} --verbose={args.verbose}  --db={args.db} --prune"
        untimed_run(c, args.norun)
        numSims = numSims + 1

    print(f"Number of Simulations {numSims}")
    print("permute-cptsize.py completed normally")

#EOF
