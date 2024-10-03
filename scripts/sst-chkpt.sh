#!/bin/bash

# This script is intended to be run in CMakeLists.txt located in tests directories
# where checkpoints are generated.
# 
# If tests that generate checkpoints are run repeatedly, sst will create a directory
# for each run.
# 
# This script deletes the 'first' directory but will leave other 
# directories (with numeric suffix) alone. Then the targeted sst
# command will be run.

# Usage: sst-chkpt {checkpoint prefix} {rest of sst options}

if [ -d $1 ]; then
    echo "WARNING: removing $1"
    rm -rf ${1}
fi

args=${@:2:$#}
echo sst --checkpoint-prefix=$1 $args
sst --checkpoint-prefix=$1 $args

#EOF

