#!/bin/bash
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
#OPTS+=" --seq=BASE_CPT"
OPTS+=" --seq=BASE_CPT_RST"
# OPTS+=" --seq=BASE_PLOAD"

# edit these to select which groups to run
do_strong_scaling=true
do_weak_scaling=true
do_component_sweeps=false

if [[ $do_strong_scaling == true ]]; then
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py strong_scaling_1to12_threads  --jobname="ss1t" ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py strong_scaling_1to12_ranks    --jobname="ss1r" ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py strong_scaling_13to40_threads --jobname="ss13t" ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py strong_scaling_13to40_ranks   --jobname="ss13r" ${OPTS}
fi

# Beware: The build time grows expontially with numComps. These will instantiate numComps * ranks * threads
if [[ $do_weak_scaling == true ]]; then
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py weak_scaling_1to12_threads  --jobname="ws1t"  --numComps=10 ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py weak_scaling_1to12_ranks    --jobname="ws1r"  --numComps=10 ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py weak_scaling_13to40_threads --jobname="ws13t" --numComps=10 ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py weak_scaling_13to40_ranks   --jobname="ws13r" --numComps=10 ${OPTS}
fi

# These take a VERY long time
if [[ $do_component_sweeps == true ]]; then
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py 2to12_ranks_100to200_components   --jobname="c100r2" ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py 2to12_threads_100to200_components --jobname="c100t2" ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py 13to40_ranks_100to200_components   --jobname="c100r13" ${OPTS}
  ${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py 13to40_threads_100to200_components --jobname="c100t13" ${OPTS}
fi

# simple sql script to extract some good info
cat << EOF > noodle.sql
.headers on
.mode csv

# base, checkpoint, restart on individual rows
CREATE TEMP TABLE raw AS
SELECT
  J.*, S.*, T.*, F.*
FROM job_info J
LEFT JOIN
  sdl_info    S ON S.jobid = J.jobid
LEFT JOIN
  timing_info T ON T.jobid = J.jobid
LEFT JOIN
  file_info   F ON F.jobid = J.jobid;

.output raw.csv
SELECT * FROM raw;

CREATE TEMP TABLE short AS
SELECT
  jobname, jobid, jobtype, friend, ranks, threads, cpt_num, cpt_timestamp, sst_version,
  disk_usage,
  global_active_activities, global_current_tv_depth, global_max_io_in, global_max_io_out,
  global_max_rss, global_max_sync_data_size, global_max_tv_depth, global_mempool_size,
  global_pf, global_sync_data_size, local_max_pf, local_max_rss, max_build_time,
  max_mempool_size, max_run_time, max_total_time, ranks, simulated_time_ua,
  clocks, bytesPerClock, msgPerClock, numComps, portsPerComp, rngSeed 
FROM
  raw;

# Combine base and checkpoint runs into single rows (currently skipping RST data)
CREATE TEMP TABLE base AS SELECT * FROM short WHERE jobtype=='BASE';
CREATE TEMP TABLE cpt  AS SELECT * FROM short WHERE jobtype=='CPT';
CREATE TEMP TABLE base_cpt AS
SELECT
  B.*, C.*
FROM base as B
LEFT JOIN
  cpt C ON B.jobid==C.friend;

# Now simply write out individual run data


# strong_scaling_1to12_threads, strong_scaling_13to40_threads
.output ss_t1to40.csv
SELECT
  * FROM base_cpt
WHERE
  jobname=='ss1t' OR jobname=='ss13t';

# strong_scaling_1to12_t_ranks, strong_scaling_13to40_ranks
.output ss_r1to40.csv
SELECT
  * FROM base_cpt
WHERE
  jobname=='ss1r' OR jobname=='ss13r';

# weak_scaling_1to12_threads, weak_scaling_13to40_threads
.output ws_t1to40.csv
SELECT
  * FROM base_cpt
WHERE
  jobname=='ws1t' OR jobname=='ws13t';

# weak_scaling_1to12_ranks, weak_scaling_13to40_ranks
.output ws_r1to40.csv
SELECT
  * FROM base_cpt
WHERE
  jobname=='ws1r' OR jobname=='ws13r';

# 2to12_threads_100to200_components, 13to40_threads_100to200_components
.output c100_t2to40.csv
SELECT
  * FROM base_cpt
WHERE
  jobname=='c100t2' OR jobname=='c100t13';

# 2to12_ranks_100to200_components, 13to40_ranks_100to200_components
.output c100_r2to40.csv
SELECT
  * FROM base_cpt
WHERE
  jobname=='c100r2' OR jobname=='c100r13';

EOF

# generate csv files
sqlite3 noodle.db < noodle.sql

#EOF