#!/bin/bash
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details

# These sweeps utilize sbatch to manage simulations using slurm

# usage:   ./run-sweeps-slurm.sh [sst-sweeper options]
# example: ./run-sweeps-slurm.sh --norun

/bin/rm -rf jobs/* hpe-phold.db hpe-phold.csv hpe-phold.sql
mkdir -p jobs || exit 1

OPTS="--noprompt --slurm $1"

# uncomment desired sequence
# OPTS+=" --seq=BASE"
#OPTS+=" --seq=BASE_CPT"
OPTS+=" --seq=BASE_CPT_RST"
# OPTS+=" --seq=BASE_PLOAD"

# edit these to select which groups to run
do_4node_sweeps=true
do_1node_sweeps=false

do_strong_scaling=false
do_weak_scaling=true
do_component_sweeps=true

if [[ $do_strong_scaling == true ]]; then
  if [[ $do_4node_sweeps == true ]]; then
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py strong_scaling_4nodes_12to40_ranks_per_node   --jobname="ssn4r12" --height=10 --nodeclamp=4 ${OPTS}
  fi
  if [[ $do_1node_sweeps == true ]]; then
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py strong_scaling_1to12_threads  --jobname="ss1t" ${OPTS}
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py strong_scaling_1to12_ranks    --jobname="ss1r" ${OPTS}
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py strong_scaling_13to40_threads --jobname="ss13t" ${OPTS}
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py strong_scaling_13to40_ranks   --jobname="ss13r" ${OPTS}
  fi
fi

# Beware: The build time grows expontially with height. These will instantiate height * ranks * threads
if [[ $do_weak_scaling == true ]]; then
  if [[ $do_4node_sweeps == true ]]; then
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py weak_scaling_4nodes_12to40_ranks_per_node   --jobname="wsn4r12" --height=10 --nodeclamp=4 --height=10 ${OPTS}
  fi
  if [[ $do_1node_sweeps == true ]]; then
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py weak_scaling_1to12_threads  --jobname="ws1t"  --height=10 ${OPTS}
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py weak_scaling_1to12_ranks    --jobname="ws1r"  --height=10 ${OPTS}
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py weak_scaling_13to40_threads --jobname="ws13t" --height=10 ${OPTS}
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py weak_scaling_13to40_ranks   --jobname="ws13r" --height=10 ${OPTS}
  fi
fi

# These take a VERY long time
if [[ $do_component_sweeps == true ]]; then
  if [[ $do_4node_sweeps == true ]]; then
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py 4nodes_12to40_ranks_per_node_100to200_components   --jobname="n4c100r12" --nodeclamp=4 ${OPTS}
  fi
  if [[ $do_1node_sweeps == true ]]; then
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py 2to12_ranks_100to200_components   --jobname="c100r2" ${OPTS}
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py 2to12_threads_100to200_components --jobname="c100t2" ${OPTS}
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py 13to40_ranks_100to200_components   --jobname="c100r13" ${OPTS}
    ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./phold_dist.py 13to40_threads_100to200_components --jobname="c100t13" ${OPTS}
  fi
fi

# simple sql script to extract some good info
cat << EOF > hpe-phold.sql
.headers on
.mode csv
.output hpe-phold.csv

SELECT
  J.jobid, J.jobname, J.jobtype,
  S.*,
  T.ranks, T.threads, T.max_build_time, T.max_run_time, T.global_max_rss
FROM job_info J
LEFT JOIN
  sdl_info    S ON S.jobid = J.jobid
LEFT JOIN
  timing_info T ON T.jobid = J.jobid

EOF

# generate hpe-phold.csv
sqlite3 hpe-phold.db < hpe-phold.sql

# print the data
cat hpe-phold.csv
