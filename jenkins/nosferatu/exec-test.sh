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

#-- EOF
