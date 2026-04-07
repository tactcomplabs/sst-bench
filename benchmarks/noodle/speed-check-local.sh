#!/bin/bash
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# speed-check.sh
# Run simulations with 8 ranks and 8 threads (with and without mpi).
# Visually check results since older versions have changed timing output strings
#

if [[ $(uname -o) =~ [Dd]arwin ]]; then
    MPIOPTS=""
else
    MPIOPTS="--bind-to socket"
fi

CLOCKS=300000

echo "########"
echo "sst -n 8"
echo "########"

rm -rf sst-n8; mkdir sst-n8 || exit 1
( cd sst-n8 && sst ../noodle-bench.py --num-threads=8 --output-json=config.json --output-partition --print-timing-info -- --verbose=0 --numComps=100 --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=${CLOCKS} --rngSeed=3131 | tee log )

doit () {
    NP=$1
    N=$2
    echo "########################"
    echo "mpi ${MPIOPTS} -np ${NP} sst -n ${N}"
    echo "########################"
    DIR=mpi-np${NP}-n${N}
    rm -rf $DIR; mkdir $DIR || exit 1
    ( cd ${DIR} && mpirun $MPIOPTS -np $NP sst ../noodle-bench.py --num-threads=$N --output-json=config.json --output-partition --print-timing-info -- --verbose=0 --numComps=100 --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=${CLOCKS} --rngSeed=3131 | tee log )
}

#   ranks threads/rank
doit  8 1
doit  1 8
