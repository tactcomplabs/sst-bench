#!/bin/bash -x
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details

# These sweeps use mpirun to manage simulations locally

# usage:   ./run-sweeps-local.sh [sst-sweeper options]
# example: ./run-sweeps-local.sh --norun

/bin/rm -rf jobs/* noodle.db noodle.csv noodle.sql
mkdir -p jobs || exit 1

OPTS="--noprompt $1"

# uncomment desired sequence
# OPTS+=" --seq=BASE"
OPTS+=" --seq=BASE_CPT"
# OPTS+=" --seq=BASE_CPT_RST"
# OPTS+=" --seq=BASE_PLOAD"

# edit these to select which groups to run
do_strong_scaling=true
do_component_sweeps=true

if [[ $do_strong_scaling ]]; then
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py strong_scaling_1to12_threads  --jobname="ss1t" ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py strong_scaling_1to12_ranks    --jobname="ss1r" ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py strong_scaling_13to40_threads --jobname="ss13t" ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py strong_scaling_13to40_ranks   --jobname="ss13r" ${OPTS}
fi

if [[ $do_component_sweeps ]]; then
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py 2to12_ranks_100to200_components   --jobname="c100r2" ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py 2to12_threads_100to200_components --jobname="c100t2" ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py 13to40_ranks_100to200_components   --jobname="c100r13" ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py 13to40_threads_100to200_components --jobname="c100t13" ${OPTS}
fi

# simple sql script to extract some good info
cat << EOF > noodle.sql
.headers on
.mode csv
.output noodle.csv

SELECT
  J.jobid, J.jobtype,
  S.numComps, S.portsPerComp, S.msgPerClock, S.bytesPerClock, S.clocks, S.rngSeed,
  T.ranks, T.threads, T.max_build_time, T.max_run_time, T.global_max_rss
FROM job_info J
LEFT JOIN
  sdl_info    S ON S.jobid = J.jobid
LEFT JOIN
  timing_info T ON T.jobid = J.jobid

EOF

# generate noodle.csv
sqlite3 noodle.db < noodle.sql

# print the data
cat noodle.csv
