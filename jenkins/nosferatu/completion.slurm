#!/bin/bash
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -A tcl
#SBATCH --partition normal

export OMPI_MCA_orte_base_help_aggregate=0

# 
# Command line options
# 
usage() { 
    echo "Usage: sbatch --dependency=singleton --job-name={jobName} completion.slurm [-d sqllite3.db] [-p]
    -d specify sqlite3 database file
    -r full path to script directory
    -p delete (prune) run directory when simulation completes" 1>&2
    -R full path to run directory
    exit 1
}

while getopts "pd:r:R:h" opt; do
    case $opt in
        h)
            usage
            ;;
        d)
            DB="${OPTARG}"
            ;;
        p)
            PRUNE=1
            ;;
        r)
            SCRIPTS="${OPTARG}"
            ;;
        R)
            RUNDIR="${OPTARG}"
            ;;    
        *)
            usage
            ;;
    esac
done

# No additional arguments allowed
shift $((OPTIND - 1))
if [ $# -gt 0 ]; then  
    usage
fi

#
# Navigate to job run directory following convention
#
# RUNDIR=/scratch/${USER}/jobs/${SLURM_JOB_NAME}
RUNDIR=${RUNDIR}/${SLURM_JOB_NAME}
cd ${RUNDIR} || exit 1

#
# File info from run
#

echo "Disk Usage"
du -h -d 1

echo "List checkpoint directories"
find . -name '[1-9]*_[1-9]*' | xargs ls -l

echo -n "Number of checkpoint directories: "
find . -name '[1-9]*_[1-9]*' | wc -l

echo -n "Number of checkpoint bin files: "
find . -name '*[0-9]*.bin' | wc -l

if [ ! -z $PRUNE ]; then
    a=$(ls -d [1-9]*) && echo "[completion.slurm] removing job directories: $a" && rm -rf $a
fi

echo "[completion.slurm] ${SLURM_JOB_NAME} jobs have completed. See ${RUNDIR}"

wait

