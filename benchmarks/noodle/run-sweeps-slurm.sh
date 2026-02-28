#!/bin/bash -x
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details

# These simulations target a single node and can be launched by sbatch.
# That is, these do not use the --slurm option of sst-sweeper.py and 
# will directly invoke mpirun on the allocated node

/bin/rm -rf jobs/* noodle.db noodle.csv noodle.sql

OPTS="--noprompt --slurm"
${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py strong_scaling_1to10_threads  ${OPTS}
${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py strong_scaling_1to10_ranks    ${OPTS}
${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py strong_scaling_11to50_threads ${OPTS}
${SST_BENCH_HOME}/scripts/sst-sweeper.py ./perf-sweeps.json ./noodle-bench.py strong_scaling_11to50_ranks   ${OPTS}

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
WHERE J.jobtype == 'BASE'

EOF

# generate noodle.csv
sqlite3 noodle.db < noodle.sql

# print the data
cat noodle.csv
