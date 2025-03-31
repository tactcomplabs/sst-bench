#!/usr/bin/env python3 

#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
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
import sqlite3
import sys
import time

class sqldb():
    def __init__(self, args, pfx):
        self.pfx = pfx
        self.con = sqlite3.connect(args.db)
        self.cur = self.con.cursor()
        qy = "CREATE TABLE IF NOT EXISTS siminfo (id INTEGER PRIMARY KEY AUTOINCREMENT, clocks, mindelay, maxdelay, mindata, maxdata, numbytes, simperiod, wallperiod, ranks, rngseed, threads, x, y, pfx, cmd)"
        self.cur.execute(qy)
        data = ( None, args.clocks, args.minDelay, args.maxDelay, args.minData, args.maxData, args.numBytes, 
                args.simPeriod, args.wallPeriod, args.ranks, args.rngSeed, args.threads, args.x, args.y, pfx, str(sys.argv))
        self.cur.execute("INSERT INTO siminfo VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
        self.cur.execute("CREATE TABLE IF NOT EXISTS chkpnt (id INTEGER PRIMARY KEY AUTOINCREMENT, simid, basetime, cpttime, basecmd, cptcmd )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS restart (id INTEGER PRIMARY KEY AUTOINCREMENT, simid, cptname, size, simtime, cmd )")
        self.con.commit()
        self.id = self.cur.execute("SELECT MAX(id) FROM siminfo").fetchone()[0]    
        print(f"Simulation ID = {self.id}")


    def __del__(self):
        self.con.close()
    
    def timed_run(self, cmd, key):
        print(cmd, flush=True)
        start = time.perf_counter()
        rc = os.system(cmd)
        etime = time.perf_counter() - start;
        if rc != 0:
            print(f"Error: rc={rc} cmd={cmd}")
            sys.exit(1)
        print(f"#TIME {key}:{etime}", flush=True)
        return etime

    def base_run(self, cmd):
        self.base = ( cmd, self.timed_run(cmd, f"base_{self.pfx}"))

    def cpt_run(self, cmd):
        self.cpt = ( cmd, self.timed_run(cmd, f"cpt_{self.pfx}"))
        # id INTEGER PRIMARY KEY, simid, basetime, cpttime, basecmd, cptcmd
        data = (None, self.id, self.base[1], self.cpt[1], self.base[0], self.cpt[0])
        self.cur.execute("INSERT INTO chkpnt VALUES(?, ?, ?, ?, ?, ?)", data)
        self.con.commit()

    def restart_run(self, cmd, cptname, cptsize):
        cptkey=f"{self.pfx}_{cptname}"
        print(f"#CPT {cptkey}:{cptsize}", flush=True);
        rst = ( cmd, self.timed_run(cmd, f"rst_{cptkey}") )
        # id INTEGER PRIMARY KEY, simid, cptname, size, simtime, cmd
        data = (None, self.id, cptname, cptsize, rst[1], rst[0])
        self.cur.execute("INSERT INTO restart VALUES(?, ?, ?, ?, ?, ?)", data)
        self.con.commit()

def untimed_run(cmd):
    print(cmd, flush=True)
    rc = os.system(cmd)
    if rc != 0:
        print(f"Error: rc={rc} cmd={cmd}")
        sys.exit(1)

if __name__ == '__main__':
    print(' '.join(sys.argv))
    parser = argparse.ArgumentParser(
        prog='restart-all.py',
        description='run 2d grid checkpoint/restart test',
        epilog='Results will be appended to to sqlite3 database file, restart.db')
    parser.add_argument("--clocks", type=int, help="number of clocks to run sim [10000]", default=10000)
    parser.add_argument("--db", type=str, help="sqlite database file [restart-all.db]", default="restart-all.db")
    parser.add_argument("--prune", action="store_true", help="remove check checkpoint data files when done")
    parser.add_argument("--minDelay", type=int, help="min number of clocks between transmissions [50]", default=50)
    parser.add_argument("--maxDelay", type=int, help="max number of clocks between transmissions [100]", default=100)
    parser.add_argument("--minData", type=int, help="Minimum number of dwords transmitted per link [10]", default=10)
    parser.add_argument("--maxData", type=int, help="Maximum number of dwords transmitted per link [256]", default=256)
    parser.add_argument("--numBytes", type=int, help="Internal state size (4 byte increments) [16384]", default=16384)
    parser.add_argument("--pdf", action="store_true", help="generate network graph pdf")
    parser.add_argument("--schema", action="store_true", help="generate checkpoint schema (requires sst-core/schema branch)")
    parser.add_argument("--simPeriod", type=int, help="time in ns between checkpoints. 0 disables. [0]", default=0)
    parser.add_argument("--wallPeriod", type=str, help="time %%H:%%M:%%S between checkpoints. 0 disables. [None]", default=None)
    parser.add_argument("--ranks", type=int, help="specify number of mpi ranks [1]", default=1)
    parser.add_argument("--rngSeed", type=int, help="seed for random number generator [1223]", default=1223)
    parser.add_argument("--threads", type=int, help="number of sst threads per rank [1]", default=1)
    parser.add_argument("--verbose", type=int, help="sst verbosity level [1]", default=1)
    parser.add_argument("--x", type=int, help="number of horizonal components [2]", default=2)
    parser.add_argument("--y", type=int, help="number of vertical components [1]", default=1)

    args = parser.parse_args()
    for arg in vars(args):
        print("\t", arg, " = ", getattr(args, arg))

    if args.simPeriod>0 and args.wallPeriod!=None:
        print("simPeriod and wallPeriod are mutually exclusive")
        sys.exit(1)
    if (args.simPeriod==0 and args.wallPeriod==None):
        print("One of simPeriod or wallPeriod must be set")
        sys.exit(1)


    ns = args.clocks

    if args.simPeriod > 0:
        periodPfx = f"sp{args.simPeriod}"
        periodOpts = f"--checkpoint-sim-period={args.simPeriod}ns"
    else:
        periodPfx = f"wp{args.wallPeriod}"
        periodOpts = f"--checkpoint-wall-period={args.wallPeriod}"
        
    pfx = f"_cpt_x{args.x}y{args.y}r{args.ranks}t{args.threads}c{args.clocks}{periodPfx}"
    pfx = f"{pfx}d{args.minData}_{args.maxData}_{args.minDelay}_{args.maxDelay}_{args.numBytes}"
    pfx = f"{pfx}_{args.rngSeed}"
    if os.path.isdir(pfx):
        shutil.rmtree(pfx)

    cptopts = f"--checkpoint-prefix={pfx} {periodOpts}"
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

    schema = ""
    if args.schema == True:
        schema = "--gen-checkpoint-schema"
        
    threadopts=""
    if args.threads>1:
        threadopts = f"-n {args.threads}"

    mpiopts=""
    if args.ranks>1:
        mpiopts = f"mpirun -n {args.ranks} --use-hwthread-cpus"

    # everything is set up. Create the database
    db = sqldb(args, pfx)

    # Baseline 
    cmd=f"{mpiopts} sst {sstopts} {dotopts} {schema} {threadopts} 2d.py -- {progopts}"
    db.base_run(cmd)

    cmd=f"{mpiopts} sst  {cptopts} {sstopts} {dotopts} {schema} {threadopts} 2d.py -- {progopts}"
    db.cpt_run(cmd)

    if args.pdf == True:
        print(f"Generating {pfx}.pdf")
        cmd = f"dot -Tpdf {pfx}.dot -o {pfx}.pdf"
        untimed_run(cmd)

    # Sometimes using sst threads we get a checkpoint file past the end of the simulation.
    cpts=glob.glob(f"{pfx}/*/*.sstcpt")
    print(f"{cpts} checkpoints generated")

    if args.simPeriod > 0:
        cpts_expected = int(ns/args.simPeriod)
    # else: TODO
    #     cpts_expected = int(db.base/args.wallPeriod)

    # TODO
    # if len(cpts) != cpts_expected and len(cpts) != ( cpts_expected + 1 ):
    #     if (args.simPeriod>0):
    #         print(f"Error: Expected {cpts_expected} checkpoint files but found {len(cpts)}")
    #         sys.exit(2)
    #     else:
    #         #TODO Change to error
    #         print(f"Warning: Expected {cpts_expected} checkpoint files but found {len(cpts)}")

    if args.simPeriod>0 and len(cpts) != cpts_expected and len(cpts) != ( cpts_expected + 1 ):
        print(f"Error: Expected {cpts_expected} checkpoint files but found {len(cpts)}")
        sys.exit(2)

    pat=re.compile(f"(.*/.*)+/{pfx}_(.+).sstcpt$")
    for cpt in cpts:
        # Determine checkpoint file name
        m=pat.match(cpt)
        if m != None:
            cptname=m.group(m.lastindex)
        else:
            print("Error: Could not determine name of checkpoint for {cpt}")
            sys.exit(1)

        # Determine size of checkpoint directory
        p=os.path.dirname(cpt)
        cptsize =  sum(os.path.getsize(f"{p}/{f}") for f in os.listdir(p) if os.path.isfile(f"{p}/{f}"))
        # Restart from checkpoint
        cmd=f"{mpiopts} sst --load-checkpoint {cpt} {threadopts}"
        db.restart_run(cmd, cptname, cptsize)       

    # optional cleaning
    if args.prune == True and os.path.isdir(pfx):
        print(f"Removing {pfx}", flush=True)
        shutil.rmtree(pfx)

    print("restart-all.py completed normally")

#EOF




