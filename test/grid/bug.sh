#!/bin/bash

x=2
y=2

echo "####################################################################"
echo "Running without MPI, 5000ns checkpointing."
echo "####################################################################"
sst  --checkpoint-prefix=bug_SAVE_ --checkpoint-period="5000ns" --add-lib-path=../../sst-bench/grid  2d.py -- --verbose=1 --x=$x --y=$y
if [[ $? != 0 ]]; then
    echo "FAILED"
    exit 1
fi 

echo "####################################################################"
echo "Running without MPI, 500ns checkpointing."
echo "####################################################################"
sst  --checkpoint-prefix=bug_SAVE_ --checkpoint-period="5000ns" --add-lib-path=../../sst-bench/grid  2d.py -- --verbose=1 --x=$x --y=$y
if [[ $? != 0 ]]; then
    echo "FAILED"
    exit 1
fi 

echo "####################################################################"
echo "Running with 2 MPI ranks, 5000ns checkpointing."
echo "####################################################################"
mpirun -n 2 sst  --checkpoint-prefix=bug_SAVE_ --checkpoint-period="5000ns" --add-lib-path=../../sst-bench/grid  2d.py -- --verbose=1 --x=$x --y=$y
if [[ $? != 0 ]]; then
    echo "FAILED"
    exit 1
fi

echo "####################################################################"
echo "Running with 2 MPI ranks, 500ns checkpointing."
echo "####################################################################"
mpirun -n 2 sst  --checkpoint-prefix=bug_SAVE_ --checkpoint-period="500ns" --add-lib-path=../../sst-bench/grid  2d.py -- --verbose=1 --x=$x --y=$y
if [[ $? != 0 ]]; then
    echo "FAILED"
    exit 1
fi

