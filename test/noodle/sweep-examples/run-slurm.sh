#!/bin/bash -x
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details

/bin/rm -rf sst-perf* timing.db *.csv *.sql

SWEEPER=$(realpath ${SST_BENCH_HOME}/scripts/sst-sweeper.py) || exit 1
JSONCFG=$(realpath ${SST_BENCH_HOME}/test/noodle/sweep.json) || exit 1
SDL=$(realpath ${SST_BENCH_HOME}/test/noodle/noodle-2d.py) || exit 1

# Do not run checkpoint and restart simulations
SEQ="--seq=BASE"
SLURM="--slurm --nodeclamp=4"
NOPROMPT="--noprompt"
$SWEEPER ${JSONCFG} ${SDL} weak_scaling_1to8threads_100bto1kb $SEQ $SLURM $NOPROMPT || exit 2

# simple sql script to extract some good info
cat << EOF > query.sql
create temp table t1 as 
    select jobid,x, bytesPerClock 
    from sdl_info;

create temp table t2 as
    select jobid, max_build_time, max_run_time, global_max_rss
    from timing_info;
    
create temp table report as
    select * from t1 left join t2 where t1.jobid=t2.jobid;

.headers on
.mode csv
.output report.csv

select * from report;
EOF

# generate report.csv
sqlite3 timing.db < query.sql

# print a few lines
head report.csv
