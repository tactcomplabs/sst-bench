#!/bin/bash

# bug test 

# sst core git info
# commit 7848d804fbdb0f936736f36b67f8f636547fd7f9 (HEAD -> master, origin/master, origin/HEAD)
# Merge: 0d412e16 1cc35cc8
# Author: SST AutoTester <sstbuilder@sandia.gov>
# Date:   Thu Oct 3 08:07:23 2024 -0600

# $ mpirun --version
# mpirun (Open MPI) 4.1.2

# OS Info
# Ubuntu 22.04.5 LTS

# test cases
#   checkpoint-period   mpi-ranks   Pass/Fail
#       None            None        Pass
#       None              2         Pass
#       5000ns          None        Pass
#       5000ns            2         Pass
#        500ns          None        Pass
#        500ns            2         Fail
#

x=2
y=2

echo "####################################################################"
echo "Running without MPI, no checkpointing."
echo "####################################################################"
sst  --add-lib-path=../../sst-bench/grid  2d.py -- --verbose=1 --x=$x --y=$y
if [[ $? != 0 ]]; then
    echo "FAILED"
    exit 1
fi

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
echo "Running with 2 MPI ranks, no checkpointing."
echo "####################################################################"
sst  --add-lib-path=../../sst-bench/grid  2d.py -- --verbose=1 --x=$x --y=$y
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

