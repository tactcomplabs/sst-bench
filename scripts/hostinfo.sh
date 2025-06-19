#!/bin/bash

# Utility for host and environment information to assist data collection
# Nothing fancy but we could massage this into key-value pairs.

echo "pwd = ${PWD}"
echo "hostname = $(hostname)"
echo "uname = $(uname -a)"
os=$(uname)
if [[ "$os" == 'Darwin' ]]; then
    hostinfo
else
    cat /proc/cpuinfo | grep 'model name' | uniq 
    procs=$(cat /proc/cpuinfo | grep processor | wc -l)
    echo "${procs} processors"
fi

printf "\nsst-core git info\n"
( cd $SST_CORE_ROOT; git status )
( cd $SST_CORE_ROOT; git log --oneline -5 )

printf "\nsst-bench git info\n"
( cd ~/work/sst-bench ; git status )
( cd ~/work/sst-bench ; git log --oneline -5 )

printf "\nEnvironment\n"
env

