#!/bin/bash

COMPS=1000
ENDCOMPS=1000000000
INTERVAL=1000
MC_LIB_PATH="../../build/components/micro-comp"
TEST="../../test/micro-comp/micro-comp-test2.py"

echo "START TEST: $COMPS to $ENDCOMPS with interval=$INTERVAL"

FILE="test.$COMPS.$ENDCOMPS.$INTERVAL.out"

touch $FILE

while [ $COMPS -le $ENDCOMPS ]
do
  echo "...loading $COMPS components"
  starttime=`date +%s.%N`
  sst --add-lib-path=$MC_LIB_PATH --model-options="--numComps $COMPS" $TEST
  endtime=`date +%s.%N`
  runtime=$( echo "$endtime - $starttime" | bc -l )
  echo $output
  echo "$COMPS $runtime" >> $FILE 2>&1
  COMPS=$(($COMPS + $INTERVAL))
done

echo "END TEST"
