#!/bin/bash -x
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#

export SLURM_CPU_BIND=verbose

SCRIPTS=$(realpath ../../scripts) || exit 1

CLOCKS=1000000
NUMCOMPS=1600
ADDLIBPATH="--add-lib-path=$(realpath ../../components/noodle)" || exit 1
SST_OPTS="--print-timing-info=4 ${ADDLIBPATH} ${PWD}/noodle-bench.py -- --verbose=0 --rngSeed=3131 --numComps=$NUMCOMPS --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=$CLOCKS"

rm -rf tmpcfg
mkdir -p tmpcfg || exit 1
TMPCFG=$(realpath tmpcfg) || exit 1

NODES=4
RANKS=160
THEADSPERRANK=1
OCFG="${TMPCFG}/r${RANKS}t${THEADSPERRANK}_.py"

sbatch --parsable --wait -N $NODES -n $RANKS -J para_init ${SCRIPTS}/perf.slurm -r ${SCRIPTS} -d ${PWD}/noodle.db -R ${PWD} sst --num-threads=$THEADSPERRANK --parallel-output --run-mode=init --output-config=${OCFG} ${SST_OPTS}

sbatch --parsable --wait -N $NODES -n $RANKS -J para_load ${SCRIPTS}/perf.slurm -r ${SCRIPTS} -d ${PWD}/noodle.db -R ${PWD} sst --num-threads=$THEADSPERRANK --parallel-load ${OCFG}
