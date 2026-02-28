#!/bin/bash
#
# ./jenkins/nosferatu/build-sst-bench-gcc13.2.0.sh
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#

# Jenkins provided parameters
# SST_SELECT

# ensure non-zero exit code in pipe propagates and no unbound variables.
set -uo pipefail

# necessary magic
export TERM=linux
export SST_BENCH_HOME=$PWD

# Be sure to launch this in top level of sst-bench (SST_BENCH_HOME)
SCRIPT_PATH=$(realpath ./jenkins/nosferatu) || ( echo "error: could not determine script path"; exit 1 )

# gcc and friends
module load cmake/3.22.1-gcc-13.2.0-qyvc7df || exit 1
export CC=gcc
export CXX=g++

# determine whether to load or build sst
if [[ -z "{SST_SELECT}" ]]; then
    echo "error: SST_SELECT is undefined" >&2
    exit 1
fi
echo "SST_SELECT=${SST_SELECT}"

if [[ ${SST_SELECT} =~ 15.1.[012] ]]; then
    module load sst/${SST_SELECT}
elif [[ ${SST_SELECT} =~ (.+)/(.+) ]]; then
    echo "Building ${SST_SELECT} locally"
    mkdir sst-install
    export INSTALL_PREFIX=$(realpath sst-install)
    echo "INSTALL_PREFIX=${INSTALL_PREFIX}"
    module load sst/dev
    SST_REPO=${BASH_REMATCH[1]}
    SST_BRANCH=${BASH_REMATCH[2]}
    git clone https://github.com/$SST_REPO/sst-core.git || exit 1
    pushd sst-core || exit 1
    git checkout ${SST_BRANCH} || exit 1
    
    ./autogen.sh || exit 1
    ./configure --prefix=${INSTALL_PREFIX} || exit 1
    make -j || exit 1
    make install || exit 1

    export PATH=${INSTALL_PREFIX}/bin:${PATH}
    hash -r
    popd
else
    echo "error: could not determine sst build from ${SST_SELECT}"
    exit 1
fi

# Build and run sst-bench
which sst || exit 1
sst --version
mkdir build || exit 1
pushd build
cmake -DSSTBENCH_ENABLE_TESTING=ON ../ || exit 1
make -j || exit 1

make test || ctest --rerun-failed --output-on-failure --verbose

popd
pushd test/noodle/sweep-examples || exit 1
./run-local.sh || exit 1

echo "sst-bench scripts completed normally"
