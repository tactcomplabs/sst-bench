#!/bin/bash
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -A tcl
#SBATCH --partition normal

# invoke after all jobs submitted using
# sbatch --dependency=singleton --job-name={jobName} completion.slurm

export OMPI_MCA_orte_base_help_aggregate=0

RUNDIR=/scratch/${USER}/jobs/${SLURM_JOB_NAME}

echo "${SLURM_JOB_NAME} jobs have completed. See ${RUNDIR}"

wait

