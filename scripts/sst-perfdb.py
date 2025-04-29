#!/usr/bin/env python3

#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# sst-perfdb.py
#

# Current restrictions:
# - All jobs are serialized. Once gizmo supports max TDP we can unleash this.
# - Hardcoded to us test/grid/2d.py. Some work needed to make more general

import argparse
import jobutils
import os
import sqlutils
import sys

from collections import OrderedDict
from copy import copy
from datetime import datetime
from enum import Enum
# from time import sleep

# globals
g_pfx = "[sst-perfdb.py]"
g_scripts = os.path.dirname(os.path.abspath(sys.argv[0]))
g_sdl = os.path.abspath(f"{g_scripts}/../test/grid/2d.py")
g_slurm_script = os.path.abspath(f"{g_scripts}/perf.slurm")
g_slurm_completion = os.path.abspath(f"{g_scripts}/completion.slurm")
g_tmpdir = f"/scratch/{os.environ['USER']}/jobs"
g_cptpfx = "_cpt"
g_start_time = datetime.now()
g_id_base = (int(datetime.timestamp(datetime.now())*10) & 0xffffff) << 16

g_sbatch="sbatch"
# g_sbatch=f"{g_scripts}/faux-sbatch.sh"
g_lid2sid = {}   # map local id to slurm id

# be gentle on gizmo
g_max_nodes = 4
g_proc_per_node = 36

class JobType(Enum):
    BASE = 1
    CPT  = 2
    RST  = 3
    COMPLETION = 4

if not os.path.isdir(g_tmpdir):
    g_tmpdir = "."

def range_arg(v):
    # command line range argument type
    try:
        values=[int(i) for i in v.split(',')]
        assert(len(values)==2 or len(values)==3)
    except (ValueError, AssertionError):
        raise argparse.ArgumentTypeError(
            f'start, end[, step]')
    if len(values)==2:
        values.append(1)
    return range(*values)

class JobEntry():
    def __init__(self, *, slurm:bool, ranks:int, threads:int, x:int, y:int, clocks:int, predecessors:list = []):
        self.jtype = JobType.BASE
        self.predecessors = predecessors
        self.ranks = ranks
        self.threads = threads
        self.procs = ranks * threads
        self.sstopts = f"--num-threads={self.threads} --output-json=config.json"
        self.sstopts += f" --print-timing-info --timing-info-json=timing.json"
        self.sdl = g_sdl
        self.sdlopts = f"-- --x={x} --y={y} --clocks={clocks}"
        self.cptid = 0
        self.cptfile = ""
        self.friend = 0
        self.cpt_num = 0
        self.cpt_timestamp = 0
        self.setdeps = False

        # nodes and processes
        self.max_nodes = g_max_nodes     
        self.max_processes = self.max_nodes * g_proc_per_node   
        if self.procs > self.max_processes:
            print(f"{self.procs} processes exceed limit of {self.max_processes}")
            sys.exit(1)
        if args.nodeclamp == 0:
            # minimize nodes
            self.nodes = 1 + int( (self.procs - 1 ) / g_proc_per_node)
            if self.nodes > self.max_nodes:
                print(f"{g_pfx} Exceeded max nodes ({self.max_nodes}) attempting {self.ranks} ranks and {self.threads} threads limiting to {g_proc_per_node} processes per node. Max processes { self.max_processes }")
                sys.exit(1)
        elif args.nodeclamp > self.max_nodes:
            print(f"{g_pfx} nodeclamp of {args.nodeclamp} exceeds max allowable nodes {self.max_nodes}")
            sys.exit(1)
        else:
            # distribute across constant node count
            self.nodes = args.nodeclamp
            print(f"{args.nodeclamp} {self.nodes} {self.procs}")
            procsPerNode = self.procs / self.nodes
            if  procsPerNode > g_proc_per_node:
                print(f"{g_pfx} {self.procs} across {self.nodes} nodes requires {procsPerNode} per node exceeding limit of {g_proc_per_node}")
                sys.exit(1)


    def cpt(self,simperiod, baseid):
        self.jtype = JobType.CPT
        self.sstopts += f" --checkpoint-prefix=_cpt --checkpoint-sim-period={simperiod}ns --checkpoint-name-format=%n_%t/grid"
        self.friend = baseid
    
    def rst(self, cptid, cptfile, cpt_num, cpt_timestamp):
        self.jtype = JobType.RST
        self.cptid = cptid
        self.cptfile = cptfile
        self.sdl = ""
        self.sdlopts = ""
        self.predecessors = [ cptid ]
        self.friend = cptid
        self.cpt_num = cpt_num
        self.cpt_timestamp = cpt_timestamp
        self.setdeps = True
    
    def completion(self):
        self.jtype = JobType.COMPLETION

    def getsid(self, slurm, lid, norun):
        if slurm:
            if lid in g_lid2sid:
                return g_lid2sid[lid]
            elif norun:
                return f":id_{lid}" # indicate dependency but sbatch will not parse it      
        return lid

    def getJobString(self, norun = False):
        # only called when submitting runs to ensure previous slurm ids are available
        if self.jtype == JobType.COMPLETION:
            jobstring = f"{g_sbatch} --parsable --wait --dependency=singleton --job-name={args.jobname} {g_slurm_completion} -r {g_scripts} -d {args.db}"
            return jobstring
        if self.jtype == JobType.RST:
            sid = self.getsid(args.slurm, self.cptid, norun)
            self.sstopts += f" --load-checkpoint ../{sid}/{self.cptfile}"
        sst_cmd = f"sst {self.sdl} {self.sstopts} {self.sdlopts}"
        if args.slurm == False:
            # local jobs will not be run in parallel so dependencies do not matter
            jobstring = f"mpirun -np {self.ranks} {sst_cmd}"
        else:
            deps = ""
            if self.setdeps and len(self.predecessors) > 0:
                deps = "--dependency=afterany"
                for lid in self.predecessors:
                    deps += f":{self.getsid(True, lid, norun)}"
            wait = "--wait"  # TODO this should be optional
            jobstring = f"{g_sbatch} --parsable {wait} {deps} -N {self.nodes} -n {self.procs} -J {args.jobname} {g_slurm_script} -r {g_scripts} -d {args.db} {sst_cmd}"
        return jobstring

class JobManager():

    def __init__(self, args):
        self.args = args
        self.next_id = g_id_base
        self.joblist = OrderedDict()
        self.wipList = []
        self.jutil = jobutils.JobUtil("jutil")
        # find a suitable temporary directory
        tdir=args.tmpdir
        if len(tdir) == 0:
            tdir = "."
        if not os.path.isdir(tdir):
                tdir = "."
        self.tmpdir = os.path.abspath(tdir)
        # determine unique job name for run directory
        self.jobname=args.jobname
        rdir=f"{self.tmpdir}/{self.jobname}"
        self.rundir=rdir
        i=0
        while os.path.isdir(self.rundir):
            i += 1
            if i >= 10000:
                print(f"{g_pfx} Unable to find unique run directory. Last checked {self.rundir}")
                sys.exit(1)
            self.rundir=f"{rdir}.{i}"
        os.makedirs(self.rundir)
        # print(f"{g_pfx} Jobs will run in: {self.rundir}")
        # database
        self.sqldb = sqlutils.sqldb(args.db, args.logging)

    def add_job(self, entry:JobEntry):
        id = self.next_id
        self.joblist[id] = entry
        self.next_id += 1
        return id
    
    def add_job_sequence(self, baseEntry:JobEntry):
        # base sim
        id_base = jobmgr.add_job(baseEntry)
        if self.args.cpt or self.args.cptrst:
            # checkpoint sim
            cptEntry=copy(baseEntry)
            cptEntry.cpt(args.simperiod, id_base)
            id_cpt = jobmgr.add_job(cptEntry)
            # predict checkpoint file names for restart
            numCpts = int(args.clocks / args.simperiod)
            period = int(args.simperiod * 1000) # ns to ps
            timestamp = (numCpts+1) * period
            if self.args.cptrst:
                # schedule shortest restart runs first 
                for n in range(numCpts, 0, -1):
                    timestamp = timestamp - period
                    # cpt = f"../{id_cpt}/{g_cptpfx}/{n}_{timestamp}/grid.sstcpt"
                    cpt = f"{g_cptpfx}/{n}_{timestamp}/grid.sstcpt"
                    rstEntry = copy(baseEntry)
                    rstEntry.rst(id_cpt, cpt, n, timestamp)
                    jobmgr.add_job(rstEntry)
        # slurm completion creates barrier and can perform post-processing
        if args.slurm:
            compEntry=copy(baseEntry)
            compEntry.completion()
            jobmgr.add_job(compEntry)

    def run(self, *, id:int, entry:JobEntry):
        jobstr = entry.getJobString(args.norun)
        print(f"{g_pfx} job {id} {jobstr}")
        if args.norun:
            return
        if args.slurm:
            cwd = "."        
            rc = self.jutil.exec(cmd=jobstr, cwd=cwd)
            if rc == 0:
                g_lid2sid[id] = self.jutil.res1
                print(f"slurm jobid = {self.jutil.res1}")
            else:
                print(f"{g_pfx} error: sbatch failed")
                sys.exit(1)
            jobid = self.jutil.res1
        else:
            cwd=f"{self.rundir}/{id}"
            rc = self.jutil.exec(cmd=jobstr, cwd=cwd, log="log")
            jobid = id

        # keep track of jobs up to completion job then run post-processing
        self.wipList.append(jobid)
        if args.slurm == False:
            self.pp_local(id=jobid, cwd=cwd)
        elif entry.jtype==JobType.COMPLETION:
            self.pp_remote(comp_id=jobid)

        # finish up with final table
        self.sqldb.job_info( jobid=jobid, dataDict={
            "friend": entry.friend,
            "jobtype": entry.jtype.name, 
            "jobstring": jobstr, 
            "slurm": args.slurm,
            "cpt_num": entry.cpt_num,
            "cpt_timestamp": entry.cpt_timestamp,
            "cwd": cwd } )
        self.sqldb.commit()

    def launch(self):
        print(f"{g_pfx} starting {len(self.joblist)} jobs in {self.rundir}")
        if self.args.noprompt == False:
            print("continue?")
            resp = input("[Yn]")
            if resp != "Y" and resp != "y":
                print("exiting...")
                sys.exit(0)

        while len(self.joblist)>0:
            j=self.joblist.popitem(False)
            self.run(id=j[0], entry=j[1])

    def pp_local(self, *, id:int, cwd:str):
        # print(f"{g_pfx} pp_local {id} {cwd}")
        self.wipList = []
        self.sqldb.file_info(jobid=id, jobpath=cwd)
        self.sqldb.timing_info(jobid=id, jobpath=cwd)
        self.sqldb.conf_info(jobid=id, jobpath=cwd)
        self.sqldb.commit()

    def pp_remote(self, comp_id:int):
        for id in self.wipList:
            if id != comp_id:
                rundir=f"{g_tmpdir}/{self.jobname}/{id}"
                cmd=f"sacct -l -j {id} --json"
                self.jutil.exec(cmd=cmd, cwd=rundir, log="slurm.json")
                self.sqldb.slurm_info(jobid=id, jobpath=rundir)
        self.sqldb.commit()
        self.wipList = []

def linear_scaling(jobmgr, args):
    # submit jobs where number of x components is proportional to the rank
    rrange = args.rrange
    ratio = args.ratio
    for r in rrange:
        X = r * ratio
        jobmgr.add_job_sequence(JobEntry(slurm=args.slurm, ranks=r, threads=1, x=X, y=1, clocks=args.clocks))

if __name__ == '__main__':

    # print(' '.join(sys.argv))

    # main parser
    parser = argparse.ArgumentParser(
        prog='sst-perfdb.py',
        description='Simulation parameter sweeps and SST performance database generation',
        epilog='This script currently requires json-timing-info branch from git@github.com:tactcomplabs/sst-core.git' )
    # common args
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--cpt", action="store_true", help="run baseline and checkpoint simulations")
    parent_parser.add_argument("--cptrst", action="store_true", help="run baseline, checkpoint, and restart simulations")
    parent_parser.add_argument("--clocks", type=int, default=1000000, help="sst clock cycles to run [1000000]")
    parent_parser.add_argument("--db", type=str, default="timing.db", help="sqlite database file to be created or updated [timing.db]")
    parent_parser.add_argument("--nodeclamp", type=int, default=0, help="distribute threads evenly across a fixed number of specified nodes. [0-minimize]")
    parent_parser.add_argument("--logging", action="store_true", help="print debug logging messages")
    parent_parser.add_argument("--jobname", type=str, default="sst-perf", help="name associated with all jobs [sst-perf]")
    parent_parser.add_argument("--norun", action="store_true", help="print job commands but do not run them")
    parent_parser.add_argument("--tmpdir", type=str, default=g_tmpdir, help=f"temporary area for running jobs. [{g_tmpdir}]")
    parent_parser.add_argument("--simperiod", type=int, default=100000, help=f"checkpoint simulation period in ns")
    parent_parser.add_argument("--slurm", action="store_true", help="launch slurm jobs instead of local ones")
    parent_parser.add_argument("--noprompt", action="store_true", help="do not prompt user to confirm launching jobs")
    # sub-parsers
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", help='available subcommands. Use {subcommand --help} for more detail')
    # linear-scaling
    parser_ls = subparsers.add_parser(
        'linear-scaling',
        help="Test with number of components proportional to number of ranks",
        parents = [parent_parser])
    parser_ls.set_defaults(func=linear_scaling)
    parser_ls.add_argument('--ratio', type=int, default=1, help='components/ranks [1]')
    parser_ls.add_argument('--rrange', type=range_arg, default=range_arg('1,8,1'), help='rank range [1,8,1]')
    
    # validate user input
    args = parser.parse_args()
    if hasattr(args, 'func') == False:
        parser.print_help()
        sys.exit(1)
    if args.clocks==0 or args.simperiod==0:
        print("clocks and simperiod must be greater than 0")
        sys.exit(1)
    if args.simperiod>=args.clocks:
        print("simperiod must be greater than clocks")
        sys.exit(1)
    # ensure we have full path to database file
    args.db = os.path.abspath(args.db)
    # log it
    if args.logging:
        for arg in vars(args):
            print(f"{g_pfx} ", arg, " = ", getattr(args, arg))

    # create job manager
    jobmgr = JobManager(args)

    # Invoke selection to set up jobs
    args.func(jobmgr, args)

    # Launch from job manager
    jobmgr.launch()
