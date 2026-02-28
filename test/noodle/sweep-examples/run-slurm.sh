#!/bin/bash -x
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details

# Using SLURM, run weak scaling test from 4 to 40 ranks on 1 node.
# Then run with ranks evenly distributed on 4 nodes.

/bin/rm -rf NODES_* slurm.db slurm.csv slurm.sql

SWEEPER=$(realpath ${SST_BENCH_HOME}/scripts/sst-sweeper.py) || exit 1
JSONCFG=$(realpath ${SST_BENCH_HOME}/test/noodle/sweep.json) || exit 1
SDL=$(realpath ${SST_BENCH_HOME}/test/noodle/noodle-2d.py) || exit 1

# Do not run checkpoint and restart simulations
SEQ="--seq=BASE"
NOPROMPT="--noprompt"
# TODO
ADDLIBPATH="--add-lib-path ${SST_BENCH_HOME}/component/noodle"
$SWEEPER ${JSONCFG} ${SDL} weak_scaling_4_40_ranks --slurm --nodeclamp=1 --jobname="NODES_1" --db="slurm.db" $SEQ $NOPROMPT || exit 2
$SWEEPER ${JSONCFG} ${SDL} weak_scaling_4_40_ranks --slurm --nodeclamp=4 --jobname="NODES_4" --db="slurm.db" $SEQ $NOPROMPT || exit 2

# simple sql script to extract some good info
cat << EOF > slurm.sql
.headers on
.mode csv
.output slurm.csv

SELECT
  J.jobid, J.jobtype, J.nodeclamp,
  S.x, S.bytesPerClock,
  T.ranks, T.threads, T.max_build_time, T.max_run_time, T.global_max_rss,
  R.jobname, R.nodes
FROM job_info J
LEFT JOIN
  sdl_info    S ON S.jobid = J.jobid
LEFT JOIN
  timing_info T ON T.jobid = J.jobid
LEFT JOIN
  slurm_info  R ON  R.jobid = J.jobid
WHERE J.jobtype = 'BASE';

EOF

# generate slurm.csv
sqlite3 slurm.db < slurm.sql

# print the data
cat slurm.csv
