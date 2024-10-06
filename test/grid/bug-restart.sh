#!/bin/bash

# restart bug test 

# sst core git info
# commit 7848d804fbdb0f936736f36b67f8f636547fd7f9 (HEAD -> master, origin/master, origin/HEAD)
# Merge: 0d412e16 1cc35cc8
# Author: SST AutoTester <sstbuilder@sandia.gov>
# Date:   Thu Oct 3 08:07:23 2024 -0600

# $ mpirun --version
# mpirun (Open MPI) 4.1.2

# OS Info
# Ubuntu 22.04.5 LTS

x=3
y=3
rm -rf restart_bug_SAVE

echo "#####################################################################"
echo "Generating checkpoints using 7 threads"
echo "#####################################################################"
sst  --checkpoint-prefix=restart_bug_SAVE --checkpoint-period=1000ns --add-lib-path=../../sst-bench/grid  -n 7 2d.py -- --verbose=1 --x=3 --y=3 --clocks=10000
if [[ $? != 0 ]]; then
    echo "FAILED checkpoint sim"
    exit 1
fi

echo "#####################################################################"
echo "Restarting from restart_bug_SAVE_8_9000000 (and repeating 100 times)"
echo "#####################################################################"
for i in {1..100}; do
    sst --load-checkpoint restart_bug_SAVE/restart_bug_SAVE_8_9000000/restart_bug_SAVE_8_9000000.sstcpt -n 7
    if [[ $? != 0 ]]; then
        echo "FAILED restart"
        exit 2
    fi
done

