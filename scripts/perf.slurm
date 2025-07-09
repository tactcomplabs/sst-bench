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
#  40 physical cores per nodes, 80 processes per node
#  72x40 = 2880 Ranks ( or 5760 using 80 )
#  Big nodes have a TByte

# NFS (home directory) is 10GbE shared
# /scratch/$USER is Infiniband

export OMPI_MCA_orte_base_help_aggregate=0

#-- module load anything you need to here
#module load openmpi4/4.1.4

#-- Command line options
usage() { 
    echo "Usage: perf.slurm -r path2Scripts -d sqlite3.db -- {commandToRun}
    -r full path to post-processing scripts
    -d full path to persistent sqlite3 database file
    -R full path to run directory
    -- {command}" 1>&2
    exit 1
}

while getopts "r:d:R:h" opt; do
    case $opt in
        h)
            usage
            ;;
        r)
            SCRIPTS="${OPTARG}"
            ;;
        d)
            DB="${OPTARG}"
            ;;
        R)
            RUNDIR="${OPTARG}"
            ;;        
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            usage
            ;;
    esac
done

#-- Remaining args is command to run
shift $((OPTIND - 1))

#-- Validate inputs
if [ -z "${SCRIPTS}" ] || [ -z "${DB}" ] || [ $# -eq 0 ]; then
    usage
fi

if [ ! -d "$SCRIPTS" ]; then
    echo "[perf.slurm] Could not locate scripts directory : ${SCRIPTS}"
    usage
fi

SQLUTIL="$SCRIPTS/sqlutils.py"
if [ ! -e "$SQLUTIL" ]; then
    echo "[perf.slurm] Could not locate sql utility script : ${SQLUTIL}"
    usage
fi

# TODO use --tmpdir
#-- cd to scratch run directory
# RUNDIR=/scratch/${USER}/jobs/${SLURM_JOB_NAME}/${SLURM_JOB_ID}
RUNDIR=${RUNDIR}/${SLURM_JOB_NAME}/${SLURM_JOB_ID}
if [ -d "${RUNDIR}" ]; then
    echo "Warning: Found ${RUNDIR}. May have stale data"
    # rm -rf ${RUNDIR}/*
else
    mkdir -p ${RUNDIR} || exit 2
fi

cd ${RUNDIR} || exit 3

# -- `prun` will execute MPI applications using the correct hosts
echo "[perf.slurm] Launching prun $*"
prun $* > log

if [ $? -ne 0 ]; then
    echo "[perf.slurm] FAILED"
    exit 6
fi

#-- generate file_info table
$SQLUTIL file-info --jobpath=${RUNDIR} --jobid=${SLURM_JOB_ID} --db=${DB}

#-- Generate timing_info table using --timing-info-json
if [ -e timing.json ]; then
    $SQLUTIL timing-info --jobpath=${RUNDIR} --jobid=${SLURM_JOB_ID} --db=${DB}
fi

#-- generate conf_info table using --output-json=config.json
if [ -e config.json ]; then
    $SQLUTIL conf-info --jobpath=${RUNDIR} --jobid=${SLURM_JOB_ID} --db=${DB}
fi

#-- slurm_info table is done by caller on management node
# sacct -l -j ${SLURM_JOB_ID} --json >> slurm.json
# $SQLUTIL slurm-info --jobpath=${RUNDIR} --jobid=${SLURM_JOB_ID} --db=${DB}

echo "Update database: ${DB}"

wait

