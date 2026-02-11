#!/usr/bin/env python3

#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
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

def is_integer(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False

def is_strict_range(s: str) -> bool:
    if is_integer(s):
        return False
    try:
        range_from_str(s)
        return True
    except (ValueError, argparse.ArgumentTypeError):
        return False
    
def range_from_str(s: str) -> range:
    # command line range argument type
    if is_integer(s):
        v = int(s)
        return range(v, v+1, 1)
    try:
        values=[int(i) for i in s.split(',')]
        assert(len(values)==2 or len(values)==3)
    except (ValueError, AssertionError):
        raise argparse.ArgumentTypeError(
            f'start, end[, step]')
    if len(values)==2:
        values.append(1)
    return range(*values)

class JobEntry():
    def __init__(self, *, sdl:str, options:list, sim_controls:list, ranks:int, threads:int, sdl_params:list, predecessors:list = []):
        
        self.jtype = JobType.BASE
        self.predecessors = predecessors
        self.ranks = ranks
        self.threads = threads
        self.procs = ranks * threads
        self.sstopts = f"--num-threads={self.threads} --output-json=config.json"
        self.sstopts += f" --print-timing-info --timing-info-json=timing.json"

        self.slurm = options['slurm']

        self.db = sim_controls['db']
        self.jobname = sim_controls['jobname']
        self.nodeclamp = int(sim_controls['nodeclamp'])

        self.cptid = 0
        self.cptfile = ""
        self.friend = 0
        self.cpt_num = 0
        self.cpt_timestamp = 0
        self.setdeps = False

        self.sdl = sdl
        self.sdlopts = "--"
        for opt in sdl_params:
            self.sdlopts += f" --{opt}={sdl_params[opt]}"
        
        # nodes and processes
        self.max_nodes = g_max_nodes     
        self.max_processes = self.max_nodes * g_proc_per_node   
        if self.procs > self.max_processes:
            print(f"{self.procs} processes exceed limit of {self.max_processes}")
            sys.exit(1)
        if self.nodeclamp == 0:
            # minimize nodes
            self.nodes = 1 + int( (self.procs - 1 ) / g_proc_per_node)
            if self.nodes > self.max_nodes:
                print(f"{g_pfx} Exceeded max nodes ({self.max_nodes}) attempting {self.ranks} ranks and {self.threads} threads limiting to {g_proc_per_node} processes per node. Max processes { self.max_processes }")
                sys.exit(1)
        elif self.nodeclamp > self.max_nodes:
            print(f"{g_pfx} nodeclamp of {self.nodeclamp} exceeds max allowable nodes {self.max_nodes}")
            sys.exit(1)
        else:
            # distribute across constant node count
            self.nodes = self.nodeclamp
            print(f"{self.nodeclamp} {self.nodes} {self.procs}")
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
            jobstring = f"{g_sbatch} --parsable --wait --dependency=singleton --job-name={self.jobname} {g_slurm_completion} -r {g_scripts} -R {g_tmpdir} -d {self.db}"
            return jobstring
        if self.jtype == JobType.RST:
            sid = self.getsid(self.slurm, self.cptid, norun)
            self.sstopts += f" --load-checkpoint ../{sid}/{self.cptfile}"
        sst_cmd = f"sst {self.sdl} {self.sstopts} {self.sdlopts}"
        if self.slurm == False:
            # local jobs will not be run in parallel so dependencies do not matter
            jobstring = f"mpirun -np {self.ranks} {sst_cmd}"
        else:
            deps = ""
            if self.setdeps and len(self.predecessors) > 0:
                deps = "--dependency=afterany"
                for lid in self.predecessors:
                    deps += f":{self.getsid(True, lid, norun)}"
            wait = "--wait"  # TODO this should be optional
            jobstring = f"{g_sbatch} --parsable {wait} {deps} -N {self.nodes} -n {self.procs} -J {self.jobname} {g_slurm_script} -r {g_scripts} -d {self.db} -R {g_tmpdir} {sst_cmd}"
        return jobstring

class JobManager():
    def __init__(self, sdl, clocks, options, sim_control_params, job_sequencer_params ):
        print("\nCreating Job Manager")
        self.clocks = clocks

        self.logging = options['logging']
        self.noprompt = options['noprompt']
        self.norun = options['norun']
        self.slurm = options['slurm']

        self.db = sim_control_params['db']
        self.jobname = sim_control_params['jobname']
        self.tmpdir = sim_control_params['tmpdir']
        self.nodeclamp = sim_control_params['nodeclamp']

        seq = job_sequencer_params['seq']
        self.do_restart = seq=='BASE_CPT_RST'
        self.do_checkpoint = seq=='BASE_CPT' or self.do_restart
        self.simperiod = int(job_sequencer_params['simperiod'])

        self.next_id = g_id_base
        self.joblist = OrderedDict()
        self.wipList = []
        self.jutil = jobutils.JobUtil("jutil")
        # determine unique job name for run directory
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
        self.sqldb = sqlutils.sqldb(self.db, self.logging)
    def add_job(self, entry:JobEntry):
        id = self.next_id
        self.joblist[id] = entry
        self.next_id += 1
        return id
    def add_job_sequence(self, baseEntry:JobEntry):
        # base sim
        id_base = jobmgr.add_job(baseEntry)
        if self.do_checkpoint:
            cptEntry=copy(baseEntry)
            cptEntry.cpt(self.simperiod, id_base)
            id_cpt = jobmgr.add_job(cptEntry)
            # predict checkpoint file names for restart
            numCpts = int(clocks / self.simperiod)
            period = int(self.simperiod * 1000) # ns to ps
            timestamp = (numCpts+1) * period
            if self.do_restart:
                # schedule shortest restart runs first 
                for n in range(numCpts, 0, -1):
                    timestamp = timestamp - period
                    cpt = f"{g_cptpfx}/{n}_{timestamp}/grid.sstcpt"
                    rstEntry = copy(baseEntry)
                    rstEntry.rst(id_cpt, cpt, n, timestamp)
                    jobmgr.add_job(rstEntry)
        # slurm completion creates barrier and can perform post-processing
        if self.slurm:
            compEntry=copy(baseEntry)
            compEntry.completion()
            jobmgr.add_job(compEntry)
    def run(self, *, id:int, entry:JobEntry):
        jobstr = entry.getJobString(self.norun)
        print(f"{g_pfx} job {id} {jobstr}")
        if self.norun:
            return
        if self.slurm:
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
        if self.slurm and friend in g_lid2sid:
            friend = g_lid2sid[entry.friend]

        # keep track of jobs up to completion job then run post-processing
        self.wipList.append(jobid)
        if self.slurm == False:
            self.pp_local(id=jobid, cwd=cwd)
        elif entry.jtype==JobType.COMPLETION:
            self.pp_remote(comp_id=jobid)

        self.sqldb.job_info( jobid=jobid, dataDict={
            "friend": friend,
            "jobtype": entry.jtype.name, 
            "jobstring": jobstr, 
            "slurm": self.slurm,
            "cpt_num": entry.cpt_num,
            "cpt_timestamp": entry.cpt_timestamp,
            "nodeclamp" : self.nodeclamp,
            "jobnodes"  : entry.nodes,
            "cwd": cwd } )
        self.sqldb.commit()
    def launch(self):
        print(f"\n{g_pfx} starting {len(self.joblist)} jobs in {self.rundir}")
        if self.noprompt == False:
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

# The json parameter settings
class JsonParams():

    def __init__(self, jsonFile: str):
        self.json = None
        self.errors = []
        self.sdl_required = ['clocks']
        self.sweep_required = ['name', 'desc', 'ranks', 'threadsPerRank']
        self.sweep_optional = ['depvar', 'sdl']
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
            for r in self.sdl_required:
                if r not in self.sdl_params:
                    self.errors.append(f"error: missing {r}' in sdl_params")
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
    def sweep_short_help(self) -> str:
        if self.json == None:
            return ""
        return f"\n{", ".join(self.sweeps.keys())}"
    def sweep_long_help(self) -> str:
        s = f"Available sweeps [{len(self.sweeps)}]\n"
        for sweep in self.sweeps:
            s += f"  {sweep}\n"
            for k in self.sweeps[sweep]:
                if k == 'name':
                    continue
                if k == 'sdl':
                    s += f"  --{k}:\n"
                    for p in self.sweeps[sweep][k]:
                        s += f"    --{p}: {self.sweeps[sweep][k][p]}\n"
                else:
                    s += f"  --{k}: {self.sweeps[sweep][k]}\n"
        return s
    def get_sweep(self, sweep):
        if sweep not in self.sweeps:
            return None
        return self.sweeps[sweep]
    def sweep_params_str(self, indent, sweep):
        if sweep not in self.sweeps:
            return ""
        lines = []
        for k in self.sweeps[sweep]:
            if k == 'name':
                continue
            if k == 'sdl':
                lines.append(f"{' ':{indent}}--{k}:")
                for p in self.sweeps[sweep][k]:
                    lines.append(f"  {' ':{indent}}--{p}: {self.sweeps[sweep][k][p]}")
            else:
                lines.append(f"{' ':{indent}}--{k}: {self.sweeps[sweep][k]}")
        return "\n".join(lines)       
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    def error_string(self) -> str:
        return f"Please fix json errors in {self.abspath}:\n" + '\n'.join(self.errors)
    def defv_str(self, group, key) -> str:
        if self.json == None:
            return ""
        if group in self.json:
            if key in self.json[group]:
                if len(self.json[group][key])==2:
                    return f"[{self.json[group][key][0]}]" # default help value string
        self.errors.append(f"error: problem with json.{group}.{key}")
        return f"[???]"

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
        usage='sst-sweeper.py jsonFile sdlFile sweep [options] [overrides]\n       sst-sweeper.py --help <path-to-jsonFile>',
        formatter_class=argparse.RawTextHelpFormatter)
    
    # positional arguments
    parser.add_argument('jsonFile', help="JSON sweeper configuration file")
    parser.add_argument('sdlFile', help="Python SST configuration file")
    parser.add_argument('sweep', help=f"Name of sweep from jsonFile {jsonParams.sweep_short_help()}")

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
                               help=f"Select simulation sequence {jsonParams.defv_str('job_sequencer', 'seq')}")
    job_seq_group.add_argument("--simperiod", type=int, 
                               help=f"checkpoint simulation period in ns {jsonParams.defv_str('job_sequencer', 'simperiod')}")
    
    # "sim_control" overrides
    sim_ctl_group = parser.add_argument_group('sim control overrides')
    sim_ctl_group.add_argument("--db", type=str, 
                               help=f"sqlite database file to be created or updated {jsonParams.defv_str('sim_controls', 'db')}")
    sim_ctl_group.add_argument("--jobname", type=str,
                               help=f"name associated with all jobs {jsonParams.defv_str('sim_controls', 'jobname')}")
    sim_ctl_group.add_argument("--tmpdir", type=str,
                               help=f"temporary area for running jobs {jsonParams.defv_str('sim_controls', 'tmpdir')}")
    sim_ctl_group.add_argument("--nodeclamp", type=int,
                               help=f"distribute threads evenly across specified nodes {jsonParams.defv_str('sim_controls', 'nodeclamp')}")

    # "sdl_params" overrides
    if jsonParams.json != None and hasattr(jsonParams,'sdl_params'):
        sdl_params_group = parser.add_argument_group(f"sdl overrides")
        sdl_params = jsonParams.sdl_params
        if sdl_params != None:
            for opt in sdl_params.keys():
                # long in tooth to provide more json validation and user visible error messages
                sdl_params_group.add_argument(f"--{opt}", type=int, 
                                              help=f"{sdl_params[opt][1]} {jsonParams.defv_str('sdl_params', opt)}")

    # help text will notify user of any malformed json checking in argument parser creation
    if jsonParams.json == None:
        parser.epilog = 'Use "--help <path-to-jsonFile>" to include custom configuration command line details (e.g. ./sst-sweeper.py --help sweep.json)'
    elif jsonParams.has_errors():
        parser.epilog = jsonParams.error_string()
    else:
        parser.epilog = jsonParams.sweep_long_help()

    # Validate positional arguments
    args = parser.parse_args()
    if not os.path.isfile(args.sdlFile):
        print(f"Could not find sdl file {args.sdlFile}")
        print(parser.usage)
        sys.exit(1)
    sdlFile = os.path.abspath(args.sdlFile)
    if jsonParams.json == None:
        print(f"Invalid json file: {args.jsonFile}")
        print(parser.usage)
        sys.exit(1)
    sweep_params = jsonParams.get_sweep(args.sweep)
    if sweep_params == None:
        print(f"error: sweep '{args.sweep}' not defined\nPlease select sweep from: {jsonParams.sweep_short_help()}\n")
        print(parser.usage)
        sys.exit(1)
    if jsonParams.has_errors():
        print(jsonParams.error_string())
        print(parser.usage)
        sys.exit(1)
    
    # collect the boolean options
    options = {
        'logging' : args.logging,
        'noprompt' : args.noprompt,
        'norun' : args.norun,
        'slurm' : args.slurm
    }

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
    print("\n[positional]")
    print(f"  {'jsonFile':<10} {os.path.abspath(args.jsonFile)}")
    print(f"  {'sdlFile':<10} {sdlFile}")
    print(f"  {'sweep':<10} {args.sweep}")
    print(jsonParams.sweep_params_str(13, args.sweep))

    print("\n[options]")
    for o in options:
        print(f"  {o:<10} {options[o]}")

    print("\n[resolved job_sequencer parameters]")
    job_sequencer_params = {}
    for key in jsonParams.job_sequencer_params:
        val = jsonParams.job_sequencer_params[key][0]
        if key in args_dict and args_dict[key] != None:
            val = args_dict[key]
        job_sequencer_params[key] = val
        print(f"  {key:<10} {val}")

    print("\n[resolved sim_controls parameters]")
    sim_control_params = {}
    for key in jsonParams.sim_control_params:
        val = jsonParams.sim_control_params[key][0]
        if key in args_dict and args_dict[key] != None:
            val = args_dict[key]
        # resolve file paths
        if key=="db" or key=="tmpdir":
            val = os.path.abspath(val)
        sim_control_params[key] = val
        print(f"  {key:<10} {val}")

    print("\n[resolved SDL parameters]")
    sdl_params = {}
    for key in jsonParams.sdl_params:
        val = jsonParams.sdl_params[key][0]
        if key in args_dict and args_dict[key] != None:
            val = args_dict[key]
        sdl_params[key] = val
        print(f"  {key:<10} {val}")

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
        clocks = int(sdl_params['clocks'])
        if clocks <= 0:
            print("error: clocks must be greater than 0")
            sys.exit(1)
        if simperiod >= clocks:
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
    # sweep dependent variable check
    depvar = None
    if 'depvar' in sweep_params:
        depvar = sweep_params['depvar']
        if depvar not in sdl_params:
            print(f"error: sweep dependent variable {depvar} not found in sdl_params")
            sys.exit(1)
        else:
            depvar_base_value = int(sdl_params[depvar])
            print(f"\nFound SDL dependent variable, '{depvar}', with base value={depvar_base_value}")
            print(f"{depvar} will be resolved as {depvar_base_value} * (ranks + threads)")
    # SDL sweep variable check
    sdl_sweep_params = None
    sdl_sweep_var = None
    sdl_sweep_range = None
    
    if 'sdl' in sweep_params:
        sdl_sweep_params = sweep_params['sdl']
        errors = 0
        for key in sdl_sweep_params:
            if key not in sdl_params:
                print(f"sdl sweep param '{key} not found in sweep sdl parameters")
                errors += 1
                continue
            val = sdl_sweep_params[key]
            if not is_strict_range(val):
                print(f"sdl key in sweep section specify a range: '{key}:{val}' is not a range")
                errors += 1
                continue
            if sdl_sweep_var==None:
                sdl_sweep_var = key
                sdl_sweep_range = range_from_str(val)
            else:
                print(f"Currently cannot have two SDL ranges: Detected ranges on '{sdl_sweep_var}' and '{key}'")
                errors += 1
                continue
        if errors > 0:
            print(f"Please fix errors in sweep sdl parameters")
            sys.exit(1)

    #
    # Job Section
    #

    # create job manager
    jobmgr = JobManager(sdlFile, sdl_params['clocks'], options, sim_control_params, job_sequencer_params)

    # Generate job descriptions and add to job manager

    # Identify rank and thread sweep ranges
    rank_sweep_range=range_from_str(sweep_params['ranks'])
    thread_sweep_range=range_from_str(sweep_params['threadsPerRank'])

    # confirm ranges
    print(f"rank sweep range:\t{rank_sweep_range}")
    print(f"thread sweep range:\t{thread_sweep_range}")
    if sdl_sweep_var != None:
        print(f"sdl {sdl_sweep_var} sweep range:\t{sdl_sweep_range}")
    else:
        sdl_sweep_range = range(1,2,1)  # placeholder for inner loop

    local_sdl_params = copy(sdl_params)
    for r in rank_sweep_range:
        for t in thread_sweep_range:
            for s in sdl_sweep_range:
                if sdl_sweep_var:
                    local_sdl_params[sdl_sweep_var] = s
                if depvar:
                    local_sdl_params[depvar] = depvar_base_value * ( r + t )
                jobmgr.add_job_sequence(JobEntry(
                    sdl=sdlFile,
                    options=options,
                    sim_controls=sim_control_params,
                    ranks=r,
                    threads=t,
                    sdl_params=local_sdl_params
                ))
    
    # Launch from job manager
    jobmgr.launch()
