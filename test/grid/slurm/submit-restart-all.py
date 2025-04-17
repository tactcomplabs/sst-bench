#!/usr/bin/env python3 

#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# submit-restart-all.py
#

import argparse
import os
import subprocess
import sys

from datetime import datetime

def submitJob(cmd):
    print(f"[submit-restart-all.py] {cmd}")
    cmdList=cmd.split(' ')
    try:
        # This works for Python3.6 used on Gizmo. Not sure about newer versions
        result = subprocess.run(cmdList, stdout=subprocess.PIPE, encoding='utf-8')
        if result.returncode != 0:
            print(f"[submit-restart-all.py] error: job submission error {result.stderr}")
            sys.exit(result.returncode)
        jobId=result.stdout.rstrip()
        print(f"[submit-restart-all.py] Submitted JobID: {jobId}")
        return jobId
    except subprocess.CalledProcessError as e:
        print(f"[submit-restart-all.py] Unable to submit job: {e}")
        print(f"[submit-restart-all.py] Command output (stderr): {e.output}")
        sys.exit(1)

if __name__ == '__main__':
    print(' '.join(sys.argv))
    parser = argparse.ArgumentParser(
        prog='submit-restart-all.py',
        description='submit 2d grid checkpoint/restart tests to slurm',
        epilog='Results will be appended to to sqlite3 database file, restart.db')
    parser.add_argument("--clocks", type=int, help="number of clocks to run sim [10000]", default=10000)
    parser.add_argument("--db", type=str, help="sqlite database file [restart-all.db]", default="restart-all.db")
    parser.add_argument("--minDelay", type=int, help="min number of clocks between transmissions [50]", default=50)
    parser.add_argument("--maxDelay", type=int, help="max number of clocks between transmissions [100]", default=100)
    parser.add_argument("--minData", type=int, help="Minimum number of dwords transmitted per link [10]", default=10)
    parser.add_argument("--maxData", type=int, help="Maximum number of dwords transmitted per link [256]", default=256)
    parser.add_argument("--numBytes", type=int, help="Internal state size (4 byte increments) [16384]", default=16384)
    parser.add_argument("--prune", action="store_true", help="remove check checkpoint data files when done")
    parser.add_argument("--rngSeed", type=int, help="seed for random number generator [1223]", default=1223)
    parser.add_argument("--verbose", type=int, help="sst verbosity level [1]", default=0)
    parser.add_argument("--x", type=int, help="number of horizonal components [2]", default=2)
    parser.add_argument("--y", type=int, help="number of vertical components [1]", default=1)
    parser.add_argument("--pdf", action="store_true", help="generate network graph pdf")
    parser.add_argument("--schema", action="store_true", help="generate checkpoint schema (requires sst-core/schema branch)")
    parser.add_argument("--sstTimingInfoJSON", action="store_true", help="enable sst experimental option --timing-info-json")

    simgroup = parser.add_mutually_exclusive_group(required=True)
    simgroup.add_argument("--simPeriod", type=int, help="time in ns between checkpoints", default=0)
    simgroup.add_argument("--wallPeriod", type=str, help="(NOT YET SUPPORTED) time in SECONDS between checkpoints. Mutually exclusive with simPeriod", default=None)

    sbatchgroup=parser.add_argument_group("sbatch")
    sbatchgroup.add_argument("--ranks", type=int, help="specify number of mpi ranks [1]", default=1)
    sbatchgroup.add_argument("--cpusPerNode", type=int, help="number of processors per node [80]", default=80)
    # sbatchgroup.add_argument("--email", type=int, help="optional email address for completion notification", default=None)
    sbatchgroup.add_argument("--maxNodes", type=int, help="maximum allowable number of nodes [30]", default=30)
    sbatchgroup.add_argument("--jobName", type=str, help="sbatch jobname [CPTRST.<datetime>]", default="CPTRST")
    parser.add_argument("--noWait", action="store_true", help="do not wait for jobs to complete [True]")

    # Don't allow sst threads
    # parser.add_argument("--threads", type=int, help="number of sst threads per rank [1]", default=1)

    args = parser.parse_args()
    for arg in vars(args):
        print("\t", arg, " = ", getattr(args, arg))

    # slurm compute nodes
    # On Gizmo, 1 node has 80 processors
    nodes=1
    if args.ranks>1:
        nodes=int(args.ranks / args.cpusPerNode) + (args.ranks % args.cpusPerNode > 1)
    if nodes > args.maxNodes:
        print(f"\n[submit-restart-all.py] error: nodes exceeds {args.maxNodes}. Use --maxNodes option to increase limit\n")
        sys.exit(1)
    
    ns = args.clocks

    if args.simPeriod > 0:
        period = int(args.simPeriod * 1000) # ns to ps
        periodPfx = f"sp{args.simPeriod}"
        periodOpts = f"--checkpoint-sim-period={args.simPeriod}ns"
    else:
        period = args.wallPeriod # must always be in seconds (unlike sst)
        periodPfx = f"wp{args.wallPeriod}"
        periodOpts = f"--checkpoint-wall-period={args.wallPeriod}"
    
    # reflect threads forced to 1 in naming convention
    # pfx = f"_cpt_x{args.x}y{args.y}r{args.ranks}t{args.threads}c{args.clocks}{periodPfx}"
    pfx = f"_cpt_x{args.x}y{args.y}r{args.ranks}t1c{args.clocks}{periodPfx}"
    pfx = f"{pfx}d{args.minData}_{args.maxData}_{args.minDelay}_{args.maxDelay}_{args.numBytes}"
    pfx = f"{pfx}_{args.rngSeed}"
    # Path name format for checkpointing                                                                 
    #  %p – prefix specified by –checkpoint-prefix                                                                                                  
    #  %t – simulated time of the checkpoint                                                                                                        
    #  %n – checkpoint number  
    cptopts = f"--checkpoint-prefix={pfx} {periodOpts} --checkpoint-name-format=%n_%t/grid"

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

    sstopts = ""
    if args.pdf == True:
        sstopts += f" --output-dot={pfx}.dot --dot-verbosity=10"

    if args.schema == True:
        sstopts += " --gen-checkpoint-schema"
    
    if args.sstTimingInfoJSON == True:
        sstopts += " --timing-info-json"

    threadopts=""
    # if args.threads>1:
    #     sstopts += f" -n {args.threads}"

    # environment variables used in grid.slurm
    os.environ['SST_GRID_SDL'] = os.path.abspath("../2d.py")

    # sbatch
    now = datetime.now()
    timestring = datetime.now().strftime("%y%m%d%H%M%S")
    jobName = f"{args.jobName}.{timestring}"
    sbatchopts=f"-J {jobName} -N {nodes} -n {args.ranks}"

    # Baseline
    cmd = f"sbatch --parsable {sbatchopts} grid.slurm {sstopts} -- {progopts}"
    jobidBase=submitJob(cmd)

    # checkpoint jobs
    # cmd = f"sbatch --dependency=afterok:{jobidBase} --parsable {sbatchopts} grid.slurm {sstopts} {cptopts} -- {progopts}"
    cmd = f"sbatch --parsable {sbatchopts} grid.slurm {sstopts} {cptopts} -- {progopts}"
    jobidCpt=submitJob(cmd)

    # restart jobs
    # Here we need to accurately predict the names of the generated files.
    # This currently only tested with friendly values of --checkpoint-sim-period.
    # Example: {pfx}/0_1000000/grid.sstcpt
    numCpts = int(args.clocks / args.simPeriod)
    ts = 0
    for n in range(1, numCpts+1):
        ts += period
        cpt = f"../{jobidCpt}/{pfx}/{n}_{ts}/grid.sstcpt"
        cmd = f"sbatch --dependency=afterok:{jobidCpt} --parsable {sbatchopts} grid.slurm --load-checkpoint {cpt}"
        jobidRst=submitJob(cmd)
  
    # Done with worker jobs
    monitorMessage=f"Monitor jobs using: sacct -X --name={jobName}"

    # Wait or no wait before exiting program
    if (args.noWait == True):
        cmd =f"sbatch --dependency=singleton --job-name={jobName} completion.slurm"
        submitJob(cmd)
        print(f"[submit-restart-all.py] All jobs submitted for {jobName}")
        print(f"[submit-restart-all.py] {monitorMessage}")
    else:
        # optional wait
        print(f"[submit-restart-all.py] Waiting on jobs for {jobName} to complete...")
        print(f"[submit-restart-all.py] {monitorMessage}")
        cmd =f"sbatch --dependency=singleton --job-name={jobName} --wait completion.slurm"
        submitJob(cmd)

    print(f"[submit-restart-all.py] Completed normally")
    
