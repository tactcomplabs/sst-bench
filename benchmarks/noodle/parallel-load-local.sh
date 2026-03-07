#!/bin/bash -x
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# parallel-load-local.sh
#

if [[ $(uname -o) =~ [Dd]arwin ]]; then
    MPIOPTS=""
else
    MPIOPTS="--bind-to socket"
fi

CLOCKS=300000
COM_OPTS="--print-timing-info=4"
SST_OPTS="--output-config=config.py ../noodle-bench.py -- --verbose=0 --rngSeed=3131 --numComps=100 --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=$CLOCKS"

echo "########"
echo "sst -n 8"
echo "########"

rm -rf sst-n8; mkdir sst-n8 || exit 1
( cd sst-n8 && sst --num-threads=8 --parallel-output --run-mode=init ${COM_OPTS} ${SST_OPTS} | tee init.log ) || exit 1
( cd sst-n8 && sst --num-threads=8 --parallel-load ${COM_OPTS} config.py | tee run.log ) || exit 1

doit () {
    NP=$1
    N=$2
    echo "########################"
    echo "mpi ${MPIOPTS} -np ${NP} sst -n ${N}"
    echo "########################"
    DIR=mpi-np${NP}-n${N}
    rm -rf $DIR; mkdir $DIR || exit 1
    ( cd ${DIR} && mpirun $MPIOPTS -np $NP sst --num-threads=$N --parallel-output --run-mode=init ${COM_OPTS} ${SST_OPTS} | tee init.log ) || exit 1
    ( cd ${DIR} && mpirun $MPIOPTS -np $NP sst --num-threads=$N --parallel-load ${COM_OPTS} config.py | tee run.log ) || exit 1
}

#   ranks threads/rank
doit  8 1
doit  1 8
