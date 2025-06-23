#!/bin/bash

#
# link-delay.sh
#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#

# example simulation setup for parameter sweep

# SST_BENCH_HOME is a required environment variable
# SST_BENCH_HOME=~/work/sst-bench
if [[ -z "${SST_BENCH_HOME}" ]]; then
    echo "error: SST_BENCH_HOME is undefined" >&2
    exit 1
fi
SST_PERFDB=$(realpath ${SST_BENCH_HOME}/scripts/sst-perfdb.py)
HOSTINFO=$(realpath ${SST_BENCH_HOME}/scripts/hostinfo.sh)

# Uncomment to use slurm job scripts
# SLURM="--slurm"

# Uncomment NORUN to see simulation commands without executing them
# NORUN="--norun"

# NAME is used in directory/file naming convention
NAME=link-delay-example

# For this example, these are fixed parameters
# components        10                          # Number of components
# link_delay        10000,11000 (random)        # Delay between link transmissions
# num_bytes         2048                        # Number of bytes per data transfer over link
# clocks            10000                       # Number of clocks to simulate
# cpt-sim-period     5000                       # Number of clocks between checkpoints

# Parameter sweep variables set with sst_perfdb command line
# drange    250 to 25 step -25     # Sweep delay clocks between link transmission.
# rrange    8 to 9 step 1          # Sweep of ranks ( fixed at 8 ranks in this case )


COMPS=40
MINDELAY=10000
MAXDELAY=11000
NUMBYTES=2048
CLOCKS=10000
SIMPERIOD=5000


# DB is the name of the sqlite database file. 
DB=timing.db

# If it exists, data is appended. Remove to recreate
rm -f $DB

# host information for management shell
#( ${HOSTINFO} > host.info ) || echo "warning: incomplete or missing host information"
${HOSTINFO} > host.info || exit 1

# Select run of baseline simulation and checkpoint simulation
# Omit --cpt to run only the baseline simulation
# CPTOPT="--cpt"
# Select run of baseline simulation, checkpoint simulation, and all restart from checkpoint simulations.
CPTOPT="--cptrst"

# Distribute threads across a fixed number of nodes (slurm only)
# CLAMP="--nodeclamp=2"

# optional temporary directory for running jobs
# JOBDIR="--tmpdir=/scratch/${USER}/jobs"

$SST_PERFDB link-delay --jobname="${NAME}" ${CPTOPT} --db="${DB}" --comps="${COMPS}" --numBytes="${NUMBYTES}" --drange=250,25,-25 --rrange=8,9,1 --clocks="${CLOCKS}" --simperiod="${SIMPERIOD}" --noprompt ${SLURM} ${NORUN} ${JOBDIR} ${CLAMP}

if [ $? != 0 ]; then
    echo "Job failed with an error"
    exit 1
fi

sqlite3 $DB < ${SST_BENCH_HOME}/examples/sql/flatten.sql

wait
