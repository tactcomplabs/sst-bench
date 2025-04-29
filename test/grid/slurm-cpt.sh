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

# Total components = RANKS
X=${RANKS}
Y=1
CLOCKS=10000
SIMPERIOD=2000
JOBNAME=cpt_${NODES}_${RANKS}
DB="$PWD"/timing.db

# last path cannot be a symlink
HOMEDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SDL=${HOEMDIR}/2d.py
SCRIPTS=$(realpath ${HOMEDIR}/../../scripts)

# configuration JSON
configInfoJSON="--output-json=config.json"

# Requires sst-core/json-timing-info branch
timingInfoJSON="--timing-info-json=timing.json"

# don't do this
# threads="--num-threads=2"
threads=""

printf "Submitting checkpoint simulation\n"
JOBID=$(sbatch --wait --parsable -N "${NODES}" -n "${RANKS}" -J "${JOBNAME}" perf.slurm -r "${SCRIPTS}" -d "${DB}" -- sst "${SDL}" "${threads}" "${configInfoJSON}" --print-timing-info "${timingInfoJSON}" --checkpoint-prefix=_cpt --checkpoint-sim-period="${SIMPERIOD}ns" --checkpoint-name-format=%n_%t/grid -- --verbose=1 --x="${X}" --y="${Y}" --clocks="${CLOCKS}")
rc=$?
if [ $rc -ne 0 ]; then
	exit $rc
fi

RUNDIR=/scratch/${USER}/jobs/${JOBNAME}/${JOBID}
printf "JOBID=${JOBID} JOBNAME=${JOBNAME} completed\n"

sacct -l -j ${JOBID} --json >> ${RUNDIR}/slurm.json
$SCRIPTS/sqlutils.py slurm-info --jobpath=${RUNDIR} --jobid=${JOBID} --db=${DB}
printf "Wrote ${RUNDIR}/slurm.json\n"

sqlite3 timing.db << EOF
.print
.tables
.headers on
.echo on

select * from jobs_info;

select * from file_info;

select * from timing_info;

select * from conf_info;

select * from slurm_info;

EOF

echo slurm-cpt.sh finished
