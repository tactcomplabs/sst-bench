#!/bin/bash
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# noodle-strong-scaling.sh
# aka, increase the thread count, but problem size remains constant
#

MODEL_OPTIONS="--portsPerComp 100 --numComps 100 --msgPerClock 8"
OUTFILE="strong-scaling.csv"
SDL="noodle-bench.py"

if [ $# -ne 2 ]; then
  echo "Usage: noodle-strong-scaling.sh MINTHREADS MAXTHREADS"
fi

if [ $1 -ge $2 ]; then
    echo "Error: MINTHREADS ($1) must be less than MAXTHREADS ($2)."
    exit 1
fi

MINT=$1
MAXT=$2

echo "Noodle Strong Scaling Config:"
echo "- MINTHREADS = $MINT"
echo "- MAXTHREADS = $MAXT"
echo "- MODEL_OPTIONS = $MODEL_OPTIONS"
echo "- OUTFILE = $OUTFILE"

if [ -f "$filename" ]; then
  rm -Rf $OUTFILE
else
  touch $OUTFILE
fi

while [ $MINT -le $MAXT ]
do
  echo "executing $MINT threads"
  TIMING=`sst -v --num-threads=$MINT --model-options="$MODEL_OPTIONS" $SDL | grep "Total time:" | awk '{print $3}'`
  echo "$MINT,$TIMING" >> $OUTFILE 2>&1
  MINT=$(($MINT + 1))
done

echo "noodle-strong-scaling complete"
