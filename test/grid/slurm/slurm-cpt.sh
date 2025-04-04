#!/bin/bash

usage() { echo "Usage: $0 -N nodes -n ranks" 1>&2; exit 1; }

while getopts "N:n:" o; do
    case $o in
	N)
	    NODES=${OPTARG}
	    ;;
	n)
	    RANKS=${OPTARG}
	    ;;
	*)
	    usage
	    ;;
    esac
done

# Validation
if [ -z "${NODES}" ] || [ -z "${RANKS}" ]; then
	usage
fi

# No additional arguments allowed
shift $((OPTIND - 1))
if [ $# -gt 0 ]; then
	usage
fi


echo NODES=$NODES
echo RANKS=$RANKS

# Total components = 2 * RANKS
X=${RANKS}
Y=2
CLOCKS=10000
SIMPERIOD=2000

printf "Submitting checkpoint simulation\n"

export SST_GRID_SDL=$(realpath ../2d.py)
id_cpt=$(sbatch --parsable -N ${NODES} -n ${RANKS} -J CHECKCPT grid.slurm  --checkpoint-prefix=_cpt --checkpoint-sim-period=${SIMPERIOD}ns --checkpoint-name-format=%n_%t/grid -- --verbose=1 --x=${X} --y=${Y} --clocks=${CLOCKS})
rc=$?
if [ $rc -ne 0 ]; then
	exit $rc
fi

printf "Job submitted with ID: $id_cpt\n\n"

echo slurm-cpt.sh finished
