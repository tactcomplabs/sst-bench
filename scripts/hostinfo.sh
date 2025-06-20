#!/bin/bash

# Utility for host and environment information to assist data collection
# Nothing fancy but we could massage this into key-value pairs.

if [[ -z "${SST_BENCH_HOME}" ]]; then
    echo "error: SST_BENCH_HOME is undefined" >&2
    exit 1
fi

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

# printf "\nsst-core git info\n"
# ( cd $SST_CORE_ROOT; git status )
# ( cd $SST_CORE_ROOT; git log --oneline -5 )

printf "\nsst-bench git info\n"
( cd ${SST_BENCH_HOME} ; git status )
( cd ${SST_BENCH_HOME} ; git log --oneline -5 )

printf "\nEnvironment\n"
env

