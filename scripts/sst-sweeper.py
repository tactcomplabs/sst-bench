#!/usr/bin/env python3

#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# sst-sweeper.py
#

import argparse
import jobutils
import json
import os
import shutil
import sqlutils
import sys

from collections import OrderedDict
from copy import copy
from datetime import datetime
from enum import Enum
from pprint import pprint
# from time import sleep

# global defaults
g_debug = False
g_version = 0.0
g_pfx = "[sst-sweeper.py]"
g_scripts = os.path.dirname(os.path.abspath(sys.argv[0]))
g_sdl = os.path.abspath(f"{g_scripts}/../test/grid/2d.py")
g_slurm_script = os.path.abspath(f"{g_scripts}/perf.slurm")
g_slurm_completion = os.path.abspath(f"{g_scripts}/completion.slurm")
g_scratchdir = os.path.abspath(".")
g_tmpdir = g_scratchdir
g_cptpfx = "_cpt"
g_start_time = datetime.now()
g_id_base = (int(datetime.timestamp(datetime.now())*10) & 0xffffff) << 16

g_sbatch="sbatch"
g_lid2sid = {}   # map local id to slurm id

# be gentle on gizmo
g_max_nodes = 4
g_proc_per_node = 36

# not all slurm systems support sacct
g_sacct = shutil.which('sacct')

class JobType(Enum):
    BASE = 1
    CPT  = 2
    RST  = 3
    COMPLETION = 4

# if scratch directory exists create a jobs directory
if not os.path.isdir(g_tmpdir):
    if os.path.isdir(g_scratchdir):
        os.mkdir(g_tmpdir)
    else:
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
    def __init__(self, *, slurm:bool, ranks:int, threads:int, x:int, y:int, clocks:int, numBytes: int, minDelay: int, maxDelay: int, predecessors:list = []):
        self.jtype = JobType.BASE
        self.predecessors = predecessors
        self.ranks = ranks
        self.threads = threads
        self.procs = ranks * threads
        self.sstopts = f"--num-threads={self.threads} --output-json=config.json"
        self.sstopts += f" --print-timing-info --timing-info-json=timing.json"
        self.sdl = g_sdl
        self.sdlopts = f"-- --x={x} --y={y} --clocks={clocks} --numBytes={numBytes} --minDelay={minDelay} --maxDelay={maxDelay}"
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
            jobstring = f"{g_sbatch} --parsable --wait --dependency=singleton --job-name={args.jobname} {g_slurm_completion} -r {g_scripts} -R {g_tmpdir} -d {args.db}"
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
            jobstring = f"{g_sbatch} --parsable {wait} {deps} -N {self.nodes} -n {self.procs} -J {args.jobname} {g_slurm_script} -r {g_scripts} -d {args.db} -R {g_tmpdir} {sst_cmd}"
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
            jobid = self.jutil.res1 # slurm job id
        else:
            cwd=f"{self.rundir}/{id}"
            rc = self.jutil.exec(cmd=jobstr, cwd=cwd, log="log")
            jobid = id

        # Post-processing: Final table updates 
        # Any records using local ids need to be converted to remote for slurm job
        # (jobid already is)
        friend = entry.friend
        if args.slurm and friend in g_lid2sid:
            friend = g_lid2sid[entry.friend]

        # keep track of jobs up to completion job then run post-processing
        self.wipList.append(jobid)
        if args.slurm == False:
            self.pp_local(id=jobid, cwd=cwd)
        elif entry.jtype==JobType.COMPLETION:
            self.pp_remote(comp_id=jobid)

        self.sqldb.job_info( jobid=jobid, dataDict={
            "friend": friend,
            "jobtype": entry.jtype.name, 
            "jobstring": jobstr, 
            "slurm": args.slurm,
            "cpt_num": entry.cpt_num,
            "cpt_timestamp": entry.cpt_timestamp,
            "nodeclamp" : args.nodeclamp,
            "jobnodes"  : entry.nodes,
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
        if g_sacct != None:
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
        jobmgr.add_job_sequence(JobEntry(slurm=args.slurm, ranks=r, threads=1, x=X, y=1, clocks=args.clocks, numBytes=args.numBytes, minDelay=args.minDelay, maxDelay=args.maxDelay))
def comp_size(jobmgr, args):
    # submit jobs where number of components is constant and we permute the data size and ranks
    rrange = args.rrange
    srange = args.srange
    X = args.comps
    for s in srange:
        for r in rrange:
            if X >= r:
                jobmgr.add_job_sequence(JobEntry(slurm=args.slurm, ranks=r, threads=1, x=X, y=1, clocks=args.clocks, numBytes=s, minDelay=args.minDelay, maxDelay=args.maxDelay))
            else:
                print(f"warning: components({X}) is less then ranks({r} ... skipped)")
def link_delay(jobmgr, args):
    # submit jobs where number of components and data size are constant. Permute link transmission delay and ranks
    # maxDelay is fixed to delay + 50
    rrange = args.rrange
    drange = args.drange
    X = args.comps
    for d in drange:
        for r in rrange:
            dmax = d + abs(drange.step)
            if X >= r:
                jobmgr.add_job_sequence(JobEntry(slurm=args.slurm, ranks=r, threads=1, x=X, y=1, clocks=args.clocks, numBytes=args.numBytes, minDelay=d, maxDelay=dmax))
            else:
                print(f"warning: components({X}) is less then ranks({r} ... skipped)")

# The json parameter settings
class JsonParams():

    def __init__(self, jsonFile: str):
        self.json = None
        self.errors = []
        self.sweep_required = ['name', 'desc', 'ranks', 'threadsPerRank']
        self.sweep_optional = ['depvar', 'factor', 'sdl']
        if jsonFile == None:
            return
        if not os.path.isfile(jsonFile):
            print(f"{g_pfx} error: could not find {jsonFile}")
            return
        self.abspath = os.path.abspath(jsonFile)
        try:
            with open(self.abspath) as f:
                self.json = json.load(f)
        except Exception as e:
            print(f"{g_pfx} error: could not load {self.abspath}: [{e}]")
            return
        if 'job_sequencer' in self.json:
            self.job_sequencer_params = self.json['job_sequencer']
        else:
            self.errors.append('error: json missing job_sequencer group')
        if 'sim_controls' in self.json:
            self.sim_control_params = self.json['sim_controls']
        else:
            self.errors.append('error: json missing sim_controls group')
        if 'sdl_params' in self.json:
            self.sdl_params = self.json['sdl_params']
        else:
            self.errors.append('error: json missing sdl_params group')
        if 'sweeps' not in self.json:
            self.errors.append('error: json missing sweeps group')
        else:
            self.sweeps = {}
            n = 0
            for sweep in self.json['sweeps']:
                key = str(n)
                if 'name' not in sweep:
                    self.errors.append(f"error: missing name in sweep '{key}'")
                else:
                    key = sweep['name']
                    self.sweeps[key] = sweep
                for r in self.sweep_required:
                    if r not in sweep and r != 'name':
                        self.errors.append(f"error: missing '{r}' in sweep '{key}'")
                # check for unknown keys
                for k in sweep:
                    if k not in self.sweep_required + self.sweep_optional:
                        self.errors.append(f"error: unknown key '{k}' in sweep '{key}'")
                n += 1

    def has_errors(self) -> bool:
        return len(self.errors) > 0
    def error_string(self) -> str:
        return f"Please fix json errors in {self.abspath}:\n" + '\n'.join(self.errors)
    def value_string(self, group, key) -> str:
        # return blank for help string when not using jsonFile
        if self.json == None:
            return ""
        if group in self.json:
            if key in self.json[group]:
                if len(self.json[group][key])==2:
                    return f"[{self.json[group][key][0]}]" # default help value string
        self.errors.append(f"error: problem with json.{group}.{key}")
        return f"[???]"
    def sweep_help(self) -> str:
        s = f"Available sweeps\n{self.sweeps}"

if __name__ == '__main__':

    # custom parser to support for '--help jsonFile'
    # otherwise, json must be the first argument
    jsonParams = JsonParams(None)
    if len(sys.argv)==3 and sys.argv[1]=='--help':
        jsonParams = JsonParams(sys.argv[2])
    elif len(sys.argv) > 2:
        jsonParams = JsonParams(sys.argv[1])
        
    # main parser
    parser = argparse.ArgumentParser(
        description='SST Simulation parameter sweeps with performance database generation',
        usage='sst=sweeper.py jsonFile sdlFile sweep [options] [overrides]\n       sst=sweeper.py --help <path-to-jsonFile>',
        formatter_class=argparse.RawTextHelpFormatter)
    
    # positional arguments
    parser.add_argument('jsonFile', help="JSON sweeper configuration file")
    parser.add_argument('sdlFile', help="Python SST configuration file")
    parser.add_argument('sweep', help="Name of sweep defined in jsonFile")

    # options
    parser.add_argument("--logging", action="store_true",
                               help=f"print logging messages")
    parser.add_argument("--noprompt", action="store_true",
                               help=f"do not prompt user to confirm launching jobs")
    parser.add_argument("--norun", action="store_true",
                               help=f"print job commands but do not run" )
    parser.add_argument("--slurm", action="store_true",
                               help=f"launch slurm jobs instead of using local mpirun")

    # "job_sequencer" overrides
    job_seq_group = parser.add_argument_group('job sequencer overrides')
    ALLOWED_SEQ = ['BASE', 'BASE_CPT', 'BASE_CPT_RST']
    job_seq_group.add_argument("--seq", type=str, choices=ALLOWED_SEQ,
                               help=f"Select simulation sequence {jsonParams.value_string('job_sequencer', 'seq')}")
    job_seq_group.add_argument("--simperiod", type=int, 
                               help=f"checkpoint simulation period in ns {jsonParams.value_string('job_sequencer', 'simperiod')}")
    
    # "sim_control" overrides
    sim_ctl_group = parser.add_argument_group('sim control overrides')
    sim_ctl_group.add_argument("--db", type=str, 
                               help=f"sqlite database file to be created or updated {jsonParams.value_string('sim_controls', 'db')}")
    sim_ctl_group.add_argument("--jobname", type=str,
                               help=f"name associated with all jobs {jsonParams.value_string('sim_controls', 'jobname')}")
    sim_ctl_group.add_argument("--tmpdir", type=str,
                               help=f"temporary area for running jobs {jsonParams.value_string('sim_controls', 'tmpdir')}")
    sim_ctl_group.add_argument("--nodeclamp", type=int,
                               help=f"distribute threads evenly across specified nodes {jsonParams.value_string('sim_controls', 'nodeclamp')}")

    # "sdl_params" overrides
    if jsonParams.json != None and hasattr(jsonParams,'sdl_params'):
        sdl_params_group = parser.add_argument_group(f"sdl overrides")
        sdl_params = jsonParams.sdl_params
        if sdl_params != None:
            for opt in sdl_params.keys():
                # long in tooth to provide more json validation and user visible error messages
                sdl_params_group.add_argument(f"--{opt}", type=int, 
                                              help=f"{sdl_params[opt][1]} {jsonParams.value_string('sdl_params', opt)}")

    # help text will notify user of any malformed json checking in argument parser creation
    if jsonParams.json == None:
        parser.epilog = 'Use "--help <path-to-jsonFile>" to include custom configuration command line details (e.g. ./sst-sweeper.py --help sweep.json)'
    elif jsonParams.has_errors():
        parser.epilog = jsonParams.error_string()
    else:
        parser.epilog = jsonParams.sweep_help()

    # Validate positional arguments
    args = parser.parse_args()
    if not os.path.isfile(args.sdlFile):
        print(f"Could not find sdl file {args.sdlFile}")
        sys.exit(1)
    if jsonParams.json == None:
        print(f"Invalid json file: {args.jsonFile}")
        sys.exit(1)
    if jsonParams.has_errors():
        print(jsonParams.error_string())
        sys.exit(1)
        
    #
    # Configuration sets defaults based on json file with command line overrides
    #
    args_dict = vars(args)
    if g_debug:
        print(f"# Command line args:")
        pprint(args_dict)
        print(f"# JSON sdl_params")
        pprint(jsonParams.sdl_params)
    
    print(f"{os.path.abspath(sys.argv[0])}\nVersion {g_version}")
    print("positional")
    print(f"  jsonFile {os.path.abspath(args.jsonFile)}")
    print(f"  sdlFile {os.path.abspath(args.sdlFile)}")

    print("options")
    print(f"   logging: {args.logging}")
    print(f"   noprompt: {args.noprompt}")
    print(f"   norun: {args.norun}")
    print(f"   slurm: {args.slurm}")

    print("resolved job_sequencer parameters")
    job_sequencer_params = {}
    for key in jsonParams.job_sequencer_params:
        v = jsonParams.job_sequencer_params[key][0]
        if key in args_dict and args_dict[key] != None:
            v = args_dict[key]
        job_sequencer_params[key] = v
        print(f"   {key}: {v}")

    print("resolved sim_controls parameters")
    sim_control_params = {}
    for key in jsonParams.sim_control_params:
        v = jsonParams.sim_control_params[key][0]
        if key in args_dict and args_dict[key] != None:
            v = args_dict[key]
        # resolve file paths
        if key=="db" or key=="tmpdir":
            v = os.path.abspath(v)
        sim_control_params[key] = v
        print(f"   {key}: {v}")

    print("resolved SDL parameters")
    sdl_params = {}
    for key in jsonParams.sdl_params:
        v = jsonParams.sdl_params[key][0]
        if key in args_dict and args_dict[key] != None:
            v = args_dict[key]
        sdl_params[key] = v
        print(f"   {key}: {v}")
    
    #
    # Resolved parameter validation
    #
    if job_sequencer_params['seq'] not in ALLOWED_SEQ:
        print(f"error: job_sequencer.seq must be in [{"|".join(ALLOWED_SEQ)}]")
    simperiod = int(job_sequencer_params['simperiod'])
    if simperiod <= 0:
        print("error: simperiod must be greater than 0")
        sys.exit(1)
    # Total simulation clocks would be nice to tag in JSON
    if 'clocks' in sdl_params:
        if sdl_params['clocks'] <= 0:
            print("error: clocks must be greater than 0")
            sys.exit(1)
        if simperiod >= sdl_params['clocks']:
            print("error: simperiod must be greater than clocks")
            sys.exit(1)
    # confirm temporary directory exists
    if not os.path.isdir(sim_control_params['tmpdir']):
        print(f"error: could not locate tmpdir: {sim_control_params['tmpdir']}")
        sys.exit(1)
    # confirm timing.db containing directory exists
    dirname = os.path.dirname(sim_control_params['db'])
    if not os.path.isdir(dirname):
        print(f"error: could not locate database (db) directory: {dirname}")
        sys.exit(1)

    # if hasattr(args, 'func') == False:
    #     parser.print_help()
    #     sys.exit(1)

    # # create job manager
    # jobmgr = JobManager(args)

    # # Invoke selection to set up jobs
    # args.func(jobmgr, args)

    # # Launch from job manager
    # jobmgr.launch()
