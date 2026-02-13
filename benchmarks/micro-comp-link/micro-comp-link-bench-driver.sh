#!/bin/bash
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# micro-comp-link-bench-driver.sh
#

THREADS=1
ENDTHREADS=41
COMPS=1
ENDCOMPS=10001
INTERVAL=10
TEST="micro-comp-link-bench.py"
FILE="test.$THREADS.$COMPS.out"
BASECOMPS=$COMPS

echo "START TEST $COMPS to $ENCDOMPS components with interval=$INTERVAL using $THREADS to $ENDTHREADS threads"

touch $FILE

while [ $THREADS -le $ENDTHREADS ]
do
  while [ $COMPS -le $ENDCOMPS ]
  do
    echo "...running benchmark using $THREADS threads and $COMPS components"
    benchstart=`date +%s.%N`
    sst --num-threads=$THREADS --model-options="--numCores $COMPS" $TEST
    benchend=`date +%s.%N`
    benchrun=$( echo "$benchend - $benchstart" | bc -l )
    echo "$THREADS $COMPS $benchstart $benchend $benchrun" >> $FILE 2>&1
    COMPS=$(($COMPS + $INTERVAL))
  done
  COMPS=$BASECOMPS
  THREADS=$(($THREADS + 1))
done

# EOF
