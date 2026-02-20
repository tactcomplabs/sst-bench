#!/bin/bash -x
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details

# Using SLURM, run weak scaling test from 4 to 40 ranks on 1 node.
# Then run with ranks evenly distributed on 4 nodes.

/bin/rm -rf sst-perf* timing.db slurm.csv *.sql

SWEEPER=$(realpath ${SST_BENCH_HOME}/scripts/sst-sweeper.py) || exit 1
JSONCFG=$(realpath ${SST_BENCH_HOME}/test/noodle/sweep.json) || exit 1
SDL=$(realpath ${SST_BENCH_HOME}/test/noodle/noodle-2d.py) || exit 1

# Do not run checkpoint and restart simulations
SEQ="--seq=BASE"
SLURM="--slurm"
NOPROMPT="--noprompt"
$SWEEPER ${JSONCFG} ${SDL} weak_scaling_4node --jobname="NODES_4" $SEQ $SLURM $NOPROMPT || exit 2
$SWEEPER ${JSONCFG} ${SDL} weak_scaling_1node --jobname="NODES_1" $SEQ $SLURM $NOPROMPT || exit 2

# simple sql script to extract some good info
cat << EOF > query.sql
create temp table t1 as 
    select jobid,x, bytesPerClock 
    from sdl_info;

create temp table t2 as
    select jobid, max_build_time, max_run_time, global_max_rss
    from timing_info;

create temp table t3 as
    select jobid, job_name, slurm_id, nodes
    from slurm_info;
    
create temp table report as
    select * from t1
    left join t2 where t1.jobid=t2.jobid
    left join t3 where t3.jobid=t3.jobid;

.headers on
.mode csv
.output slurm.csv

select * from slurm;
EOF

# generate slurm.csv
sqlite3 timing.db < query.sql

# print a few lines
head slurm.csv
