#!/bin/bash
#
# ./jenkins/nosferatu/exec-test.sh
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#

# resolve unbound variables
JOB_ID=${JOB_ID:=""}

# ensure non-zero exit code in pipe propagates and no unbound variables.
set -uo pipefail

USER=$(id -un)

#-- setup the environment
/jenkins/scripts/setup-env.sh

#-- execute the job
SCRIPT=$1
SLURM_ID=$(sbatch -N1 -p normal --export=ALL "$SCRIPT" | awk '{print $4}')

#-- wait for completion
COMPLETE=$(squeue -u "$USER" | grep "${SLURM_ID}")
while [[ -n $COMPLETE ]]; do
  sleep 1
  COMPLETE=$(squeue -u "$USER" | grep "${SLURM_ID}")
done

#-- echo the result to the log
OUTFILE="slurm-${SLURM_ID}.out"
cat ${OUTFILE}

#-- job has completed, test for status
STATE=$(grep "tests failed out of" < "${OUTFILE}")
NUM_FAILED=$(grep "tests failed out of" < "${OUTFILE}" | awk '{print $4}')

if [[ $NUM_FAILED -eq 0 ]];
then

  echo "TEST PASSED FOR JOB_ID = ${JOB_ID}; SLURM_JOB=${SLURM_ID}"
  echo "$STATE"
  #-- make sure we got to the end of the test script
  grep -s "sst-bench scripts completed normally"
  if [ $? -eq 0 ]; then
      echo "sst-bench scripts did not complete - FAIL"
      exit 1
  fi
  #-- make sure no other errors (e.g. tests did not run!)
  grep -s -i error ${OUTFILE}
  if [ $? -eq 0 ]; then
      echo "ERRORS DETECTED FOR JOB_ID = ${JOB_ID}; SLURM_JOB=${SLURM_ID}"
      exit 1
  fi
  exit 0
else
  echo "TEST FAILED FOR JOB_ID = ${JOB_ID}; SLURM_JOB=${SLURM_ID}"
  echo "$STATE"
  exit 1
fi

#-- EOF
