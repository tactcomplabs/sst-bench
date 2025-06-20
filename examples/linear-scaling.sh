#!/bin/bash

#
# linear-scaling.sh
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

# NAME is used in directory/file naming convention
NAME=linear-scaling-example

# For this example, these are fixed parameters
# link_delay        10000,11000 (random)        # Delay between link transmissions
# clocks            10000                       # Number of clocks to simulate
# cpt-sim-period     5000                       # Number of clocks between checkpoints

# Parameter sweep variables set with sst_perfdb command line
# srange    1000 to 11000 step 5000     # Number of state elements per component
# rrange    2 to 8 step 2               # Sweep of ranks

# The ratio of the number of components per rank is permuted from 1 to 10 in an outer loop

MINDELAY=10000
MAXDELAY=11000
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

# optional temporary directory for running jobs
# TMPDIR="--tmpdir=/scratch/${USER}/jobs"

# permute number of components per rank across all ranks
for r in $(seq 1 10); do
    ratio=$(( $r*1 ))
    echo
    echo "#######################"
    echo "Launching ratio $ratio "
    echo "#######################"
    echo 
    $SST_PERFDB linear-scaling --jobname="${NAME}" $CPTOPT --db="${DB}" --ratio="${ratio}" --rrange=2,9,2 --clocks="${CLOCKS}" --simperiod="${SIMPERIOD}" --noprompt  --minDelay=${MINDELAY} --maxDelay=${MAXDELAY} ${SLURM} ${NORUN} ${TMPDIR} ${CLAMP}
    if [ $? != 0 ]; then
       echo "Job failed with an error"
       exit 1
    fi
done

sqlite3 $DB < ${SST_BENCH_HOME}/examples/sql/flatten.sql

wait
