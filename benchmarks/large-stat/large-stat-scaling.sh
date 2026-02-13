#!/bin/bash

COMPS=10
ENDCOMPS=1000
INTERVAL=10
STATS=10
ENDSTATS=1000
MC_LIB_PATH="../../build/components/large-stat"
TEST1="./large-stat-bench1.py"
TEST2="./large-stat-bench2.py"

echo "START TEST: $COMPS to $ENDCOMPS with interval=$INTERVAL"

FILE="test.$COMPS.$ENDCOMPS.$INTERVAL.out"

touch $FILE

while [ $COMPS -le $ENDCOMPS ]
do

  while [ $STATS -le $ENDSTATS ]
  do
    echo "...running stats for $COMPS components and $STATS statistics per component"
    csv_starttime=`date +%s.%N`
    sst --add-lib-path=$MC_LIB_PATH --model-options="--numComps $COMPS --numStats $STATS" $TEST1
    csv_endtime=`date +%s.%N`
    csv_runtime=$( echo "$csv_endtime - $csv_starttime" | bc -l )
    echo $output

    sql_starttime=`date +%s.%N`
    sst --add-lib-path=$MC_LIB_PATH --model-options="--numComps $COMPS --numStats $STATS" $TEST2
    sql_endtime=`date +%s.%N`
    sql_runtime=$( echo "$sql_endtime - $sql_starttime" | bc -l )
    echo $output

    STATS=$(($STATS + $INTERVAL))
    echo "$COMPS $STATS $csv_runtime $sql_runtime" >> $FILE 2>&1

    rm -Rf *.csv *.sql
  done

  COMPS=$(($COMPS + $INTERVAL))
done

echo "END TEST"
