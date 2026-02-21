#!/bin/bash -x
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details

/bin/rm -rf CPTRST_LOCAL_* cptrst_local.db cptrst_local.csv cptrst_local.sql

SWEEPER=$(realpath ${SST_BENCH_HOME}/scripts/sst-sweeper.py) || exit 1
JSONCFG=$(realpath ${SST_BENCH_HOME}/test/noodle/sweep.json) || exit 1
SDL=$(realpath ${SST_BENCH_HOME}/test/noodle/noodle-2d.py) || exit 1

# Do not run checkpoint and restart simulations
SEQ="--seq=BASE_CPT_RST"
NOPROMPT="--noprompt"
# TODO
ADDLIBPATH="--add-lib-path ${SST_BENCH_HOME}/component/noodle"
$SWEEPER ${JSONCFG} ${SDL} weak_scaling_short --jobname="CPTRST_LOCAL_1" --db="cptrst_local.db" $SEQ $NOPROMPT || exit 2

# simple sql script to extract some good info
cat << EOF > cptrst_local.sql
.headers on
.mode csv
.output cptrst_local.csv

SELECT
  J.jobid, J.jobtype, J.nodeclamp,
  S.x, S.bytesPerClock,
  T.max_build_time, T.max_run_time, T.global_max_rss
FROM job_info J
LEFT JOIN
  sdl_info    S ON S.jobid = J.jobid
LEFT JOIN
  timing_info T ON T.jobid = J.jobid;

EOF

# generate cptrst_local.csv
sqlite3 cptrst_local.db < cptrst_local.sql

# print the data
cat cptrst_local.csv
