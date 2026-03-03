#!/bin/bash
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#

export SLURM_CPU_BIND=verbose

SCRIPTS=$(realpath ../../scripts) || exit 1

CLOCKS=300000
ADDLIBPATH="--add-lib-path= $(realpath ../../components/noodle)" || exit 1
SST_OPTS="--print-timing-info=4 ${ADDLIBPATH} ${PWD}/noodle-bench.py -- --verbose=0 --rngSeed=3131 --numComps=100 --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=$CLOCKS"

RANKS=8
THREADS=1
OCFG="r${RANKS}t${THREADS}.py"
sbatch --parsable --wait  -N 1 -n $RANKS -J para_init ${SCRIPTS}/perf.slurm -r ${SCRIPTS} -d ${PWD}/noodle.db -R ${PWD} sst --num-threads=$THREADS --parallel-output --run-mode=init --output-cfg=${OCFG} ${SST_OPTS}
#sbatch --parsable --wait  -N 1 -n $RANKS -J para_load ${SCRIPTS}/perf.slurm -r ${SCRIPTS} -d ${PWD}/noodle.db -R ${PWD} sst --num-threads=$THREADS --parallel-load ${OCFG}

# RANKS=1
# THREADS=8
# OCFG="r${RANKS}t${THREADS}.py"
# sbatch --parsable --wait  -N 1 -n $RANKS -J para_init ${SCRIPTS}/perf.slurm -r ${SCRIPTS} -d ${PWD}/noodle.db -R ${PWD} sst --n# um-threads=$THREADS --parallel-output --run-mode=init --output-cfg=${OCFG} ${SST_OPTS}
sbatch --parsable --wait  -N 1 -n $RANKS -J para_load ${SCRIPTS}/perf.slurm -r ${SCRIPTS} -d ${PWD}/noodle.db -R ${PWD} sst --num-threads=$THREADS --parallel-load ${OCFG}
