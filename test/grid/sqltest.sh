#!/bin/bash

SQLUTILS=$(realpath ../../scripts/sqlutils.py)
TESTDIR="sqtest-dir"

ranks=3
threads=4
x=$(( $ranks * $threads ))

sdl=$(realpath 2d.py)
rm -rf ${TESTDIR}
mkdir ${TESTDIR} || exit 1

(cd ${TESTDIR} && mpirun -n ${ranks} sst ${sdl} --verbose --num-threads=${threads} --output-json=config.json --print-timing-info --timing-info-json=timing.json --checkpoint-prefix=_cpt --checkpoint-sim-period=2000ns --checkpoint-name-format=%n_%t/grid -- --verbose=1 --x=${x} --y=1 --clocks=10000)

rundir=$(realpath ${TESTDIR})
rm -f timing.db
${SQLUTILS} timing-info --jobpath=$rundir --jobid=1 
${SQLUTILS} file-info   --jobpath=$rundir --jobid=1
${SQLUTILS} conf-info   --jobpath=$rundir --jobid=1

sqlite3 timing.db << EOF
.print
.tables
.headers on
.echo on
.print
select * from timing_info;
.print
select * from file_info;
.print
select * from conf_info;
.print
EOF
wait


