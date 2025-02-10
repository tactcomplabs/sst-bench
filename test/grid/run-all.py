#!/usr/bin/env python3

#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# run-all.py
#

import argparse
import math
import os
import platform

def untimed_run(cmd):
    print("\n###########################################################################", flush=True)
    print(cmd, flush=True)
    print("###########################################################################", flush=True)
    rc = os.system(cmd)
    if rc != 0:
        print(f"Error: rc={rc} cmd={cmd}")
        exit(rc)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="run all tests and generate performance data")
    parser.add_argument("--norun", action="store_true", help="print simulation commands but do not run")
    parser.add_argument("--short", action="store_true", help="run only up to a 2x2 grid")
    args = parser.parse_args()
    prog = "./permute-threads-xy.py"
    
    if args.short:
        cpus=2
        gridlen = 2
    else:
        cpus = os.cpu_count()
        gridlen = int(math.sqrt(cpus*10))

    print(f"Using {cpus} cpus. Setting max grid to {gridlen}x{gridlen}")

    # Suppress running so we can do a dry run of command line and find number of simulations
    norun = ""
    if args.norun == True:
        norun = "--norun"
    
    # permute x,y,threads
    cmd=f"{prog} {norun} --maxthreads={cpus} --maxrow={gridlen} --maxcols={gridlen}  --numBytes=1024 --minData=1024 --maxData=65536 --simPeriod=1000 --clocks=10000"
    untimed_run(cmd)

    # TODO 
    if platform.system() != "Darwin":
        # permute x,y,ranks
        cmd=f"{prog} {norun} --maxranks={cpus} --maxrow={gridlen} --maxcols={gridlen}  --numBytes=1024 --minData=1024 --maxData=65536 --simPeriod=1000 --clocks=10000"
        untimed_run(cmd)

    # Whew!
    print("run-all.py completed normally")
