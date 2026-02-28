#!/bin/bash
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details

# Quick check of ranks vs threads performance using slurm

export SLURM_CPU_BIND=verbose
CLOCKS=300000

SCRIPTS=$(realpath ../../scripts) || exit 1
ADDLIBPATH="--add-lib-path= $(realpath ../../components/noodle)" || exit 1

RANKS=8
THREADS=1
sbatch --parsable --wait  -N 1 -n $RANKS -J noodle_perf ${SCRIPTS}/perf.slurm -r ${SCRIPTS} -d ${PWD}/noodle.db -R ${PWD} sst ${PWD}/noodle-bench.py --num-threads=$THREADS --output-json=config.json --print-timing-info --timing-info-json=timing.json --add-lib-path=${ADDLIBPATH} -- --verbose=0 --numComps=100 --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=$CLOCKS --rngSeed=3131

RANKS=1
THREADS=8
sbatch --parsable --wait  -N 1 -n $RANKS -J noodle_perf ${SCRIPTS}/perf.slurm -r ${SCRIPTS} -d ${PWD}/noodle.db -R ${PWD} sst ${PWD}/noodle-bench.py --num-threads=$THREADS --output-json=config.json --print-timing-info --timing-info-json=timing.json --add-lib-path=${ADDLIBPATH} -- --verbose=0 --numComps=100 --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=$CLOCKS --rngSeed=3131
