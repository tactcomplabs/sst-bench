#!/bin/bash
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# noodle-weak-scaling.sh
# aka, increase the thread count and the problem size
#

MODEL_OPTIONS="--portsPerComp 100 --msgPerClock 8"
OUTFILE="weak-scaling.csv"
SDL="noodle-bench.py"
COMPBASE=100

if [ $# -ne 3 ]; then
  echo "Usage: noodle-weak-scaling.sh MINTHREADS MAXTHREADS COMPSTEP"
fi

if [ $1 -ge $2 ]; then
    echo "Error: MINTHREADS ($1) must be less than MAXTHREADS ($2)."
    exit 1
fi

MINT=$1
MAXT=$2
STEP=$3

echo "Noodle Strong Scaling Config:"
echo "- MINTHREADS = $MINT"
echo "- MAXTHREADS = $MAXT"
echo "- COMPBASE = $COMPBASE"
echo "- COMPSTEP = $STEP"
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
  TIMING=`sst -v --num-threads=$MINT --model-options="$MODEL_OPTIONS --numComps $COMPBASE" $SDL | grep "Total time:" | awk '{print $3}'`
  echo "$MINT,$COMPBASE,$TIMING" >> $OUTFILE 2>&1
  MINT=$(($MINT + 1))
  COMPBASE=$(($COMPBASE + $STEP))
done

echo "noodle-weak-scaling complete"
