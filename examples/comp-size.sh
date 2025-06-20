#!/bin/bash

#
# comp-size.sh
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
SST_PERFDB=$(realpath ${SST_BENCH_HOME}/scripts/sst-perfdb.py)
HOSTINFO=$(realpath ${SST_BENCH_HOME}/scripts/hostinfo.sh)

# Uncomment to use slurm job scripts
# SLURM="--slurm"

# Uncomment NORUN to see simulation commands without executing them
# NORUN="--norun"

# For this example, these are fixed parameters
# components        10                          # Number of components
# link_delay        10000,11000 (random)        # Delay between link transmissions
# clocks            10000                       # Number of clocks to simulate
# cpt-sim-period     5000                       # Number of clocks between checkpoints

# Parameter sweep variables set with sst_perfdb command line
# srange    1000 to 11000 step 5000     # Number of state elements per component
# rrange    2 to 8 step 2               # Sweep of ranks

COMPS=40
MINDELAY=10000
MAXDELAY=11000
CLOCKS=10000
SIMPERIOD=5000



# NAME is used in directory/file naming convention
NAME=comp-size-mpi

# DB is the name of the sqlite database file. 
DB=timing.db

# If it exists, data is appended. Remove to recreate
rm -f $DB

# host information for management shell
#( ${HOSTINFO} > host.info ) || echo "warning: incomplete or missing host information"
${HOSTINFO} > host.info || exit 1

# Select run of baseline simulation and checkpoint simulation
# CPTOPT="--cpt"
# Select run of baseline simulation, checkpoint simulation, and all restart from checkpoint simulations.
CPTOPT="--cptrst"

# optional temporary directory for running jobs
# TMPDIR="--tmpdir=/scratch/${USER}/jobs"

$SST_PERFDB comp-size --jobname="${NAME}" ${CPTOPT} --db="${DB}" --comps="${COMPS}" --srange=1000,11000,5000 --rrange=2,9,2 --clocks="${CLOCKS}" --simperiod="${SIMPERIOD}" --noprompt --minDelay="${MINDELAY}" --maxDelay="${MAXDELAY}" ${SLURM} ${NORUN} ${TMPDIR}

if [ $? != 0 ]; then
    echo "Job failed with an error"
    exit 1
fi

sqlite3 $DB < ${SST_BENCH_HOME}/examples/sql/flatten.sql

wait
