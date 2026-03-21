#!/bin/bash
#
# ./jenkins/srun/build-sst-bench-gcc13.2.0.sh
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
SCRIPT_PATH=$(realpath ./jenkins/srun) || ( echo "error: could not determine script path"; exit 1 )

# gcc and friends
module load cmake/3.22.1-gcc-13.2.0-qyvc7df || exit 1
export CC=gcc
export CXX=g++

# SST_SELECT provides <repo>/<branch> for sst-core
if [[ -z "{SST_SELECT}" ]]; then
    echo "error: SST_SELECT is undefined" >&2
    exit 1
fi
echo "SST_SELECT=${SST_SELECT}"

if [[ ! ${SST_SELECT} =~ (.+)/(.+) ]]; then
    echo "error: SST_SELECT (${SST_SELECT}) is not in <repo>/<branch> format"
fi

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

echo "Starting sst build at $(date)"
make -j || exit 1
make install || exit 1
echo "Finished sst build at $(date)"

export PATH=${INSTALL_PREFIX}/bin:${PATH}
hash -r
popd

# Build sst-bench
which sst || exit 1
sst --version
mkdir build || exit 1
pushd build
cmake -DSSTBENCH_ENABLE_TESTING=ON ../ || exit 1
echo "Starting sst-bench build at $(date)"
make -j || exit 1
echo "Finished sst-bench build at $(date)"

# Test sst-bench
ctest -LE elements || ctest --rerun-failed --output-on-failure --verbose || exit 1

echo "build-all-gcc13.2.0.sh completed normally"
