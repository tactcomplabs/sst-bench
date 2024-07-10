#!/bin/bash

COMPS=1
ENDCOMPS=100
INTERVAL=10
BASE=64
ORIGBASE=$BASE
ENDSIZE=1000000
SIZEINTERVAL=1024
RESTORE_LIB_PATH="../../build/sst-bench/restore"
TEST="single-thread-restore.py"
FILE="test.$COMPS.$ENDCOMPS.$INTERVAL.out"

echo "START TEST: $COMPS to $ENDCOMPS components with interval=$INTERVAL; $BASE to $ENDSIZE KB with interval=$SIZEINTERVAL"

touch $FILE

while [ $COMPS -le $ENDCOMPS ]
do
  while [ $BASE -le $ENDSIZE ]
  do
    echo "...loading $COMPS components with $BASE KB each"
    loadtimestart=`date +%s.%N`
    sst --add-lib-path=$MC_LIB_PATH --checkpoint-period=5us --checkpoint-prefix=single-thread --model-options="--numComps $COMPS --numKB $BASE" $TEST
    loadtimeend=`date +%s.%N`
    loadtime=$( echo "$loadtimeend - $loadtimestart" | bc -l )

    echo "...restoring $COMPS components with $BASE KB each"
    restoretimestart=`date +%s.%N`
    sst --add-lib-path=$MC_LIB_PATH --load-checkpoint ./single-thread_5000000_0.sstcpt
    restoretimeend=`date +%s.%N`
    restoretime=$( echo "$restoretimeend - $restoretimestart" | bc -l )

    echo "$COMPS $BASE $loadtime $restoretime" >> $FILE 2>&1
    rm -Rf ./*.sstcpt

    BASE=$(($BASE + $SIZEINTERVAL))
  done
  BASE=$ORIGBASE
  COMPS=$(($COMPS + $INTERVAL))
done

echo "END TEST"

