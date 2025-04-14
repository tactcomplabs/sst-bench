#!/bin/bash
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -A tcl
#SBATCH -J SSTBENCH_GRID_JOB
#SBATCH --partition normal

#-- To request 160 ranks use -N 4 -n 160 (override in sbatch command line)
#-- the `-A tcl` directive should not be changed
#-- you can change `normal` to `largemem` if you want the 1TB memory nodes (but there are currently only three)
#-- the `-J SST_JOB` will "name" the job.  That way you can see it running when you use the `squeue` command

# gizmo
#  72 nodes
#  40 physical cores per nodes
#  72x40 = 2880 Ranks
#  Big nodes have a TByte

# NFS (home directory) is 10GbE shared
# /scratch/$USER is Infiniband

export OMPI_MCA_orte_base_help_aggregate=0

# -- module load anything you need to here
#module load openmpi4/4.1.4

#-- cd to scratch run directory
RUNDIR=/scratch/${USER}/jobs/${SLURM_JOB_NAME}/${SLURM_JOB_ID}
if [ -d "${RUNDIR}" ]; then
    rm -rf ${RUNDIR}
fi
mkdir -p ${RUNDIR}
cd ${RUNDIR}

# Check required environment variables
if [ -z "${SST_GRID_SDL}" ]; then
    echo "error: SST_GRID_SDL is not set"
    exit 4
fi
if [ ! -e "${SST_GRID_SDL}" ]; then
    echo "error: Could not find ${SST_GRID_SDL}"
    exit 5
fi

# -- `prun` will execute MPI applications using the correct hosts
# -- add whatever SST options you want here
prun sst ${SST_GRID_SDL} $* > log

wait

