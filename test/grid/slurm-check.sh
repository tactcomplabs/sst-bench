#!/bin/bash

# NODES=1 # always 1
RANKS=6
THREADS=1
X=${RANKS}
Y=${THREADS}
PROCS=$(( ${RANKS} * ${THREADS} ))
CLOCKS=10000
SIMPERIOD=3000

JOBNAME=chk_${RANKS}_${THREADS}_$(( $(date +%s) % 86400 ))
DB="$PWD"/timing.db
rm -f ${DB}

# last path cannot be a symlink
HOMEDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SDL=${HOMEDIR}/2d.py
SCRIPTS=$(realpath ../../scripts)

# configuration JSON
configInfoJSON="--output-json=config.json"

# Requires sst-core/json-timing-info branch
timingInfoJSON="--timing-info-json=timing.json"

echo "Submitting base simulation"
id_base=$(sbatch --parsable -N 1 -n "${PROCS}" -J "${JOBNAME}" perf.slurm -r "${SCRIPTS}" -d "${DB}" -- sst "${SDL}" --num-threads=${THREADS} "${configInfoJSON}" --print-timing-info "${timingInfoJSON}" -- --x="${X}" --y="${Y}" --clocks="${CLOCKS}")
rc=$?
if [ $rc -ne 0 ]; then
	exit $rc
fi
echo "Job submitted with ID: $id_base"
jobs=( ${id_base} )

echo "Submitting checkpoint simulation"
id_cpt=$(sbatch --parsable -N 1 -n "${PROCS}" -J "${JOBNAME}" perf.slurm -r "${SCRIPTS}" -d "${DB}" -- sst "${SDL}" --num-threads=${THREADS} "${configInfoJSON}" --print-timing-info "${timingInfoJSON}" --checkpoint-prefix=_cpt --checkpoint-sim-period="${SIMPERIOD}ns" --checkpoint-name-format=%n_%t/grid -- --x="${X}" --y="${Y}" --clocks="${CLOCKS}")

rc=$?
if [ $rc -ne 0 ]; then
	exit $rc
fi
echo "Job submitted with ID: $id_cpt"
jobs+=( ${id_cpt} )

echo "Submitting dependent restart simulations"
# these depend on --clocks and --checkpoint-sim-period
declare -a ids=("1_3" "2_6" "3_9")
for id in "${ids[@]}"; do
    id_rst=$(sbatch --dependency=afterany:${id_cpt} --parsable -N 1 -n "${PROCS}" -J "${JOBNAME}" perf.slurm -r "${SCRIPTS}" -d "${DB}" -- sst --num-threads=${THREADS} "${configInfoJSON}" --print-timing-info "${timingInfoJSON}" --load-checkpoint ../${id_cpt}/_cpt/${id}000000/grid.sstcpt)
    rc=$?
    if [ $rc -ne 0 ]; then
        exit $rc
    fi
    echo "Job submitted with ID: $id_rst"
    jobs+=( ${id_rst} )
done

echo "Submitting completion script to wait for jobs: ${jobs[@]}"
sbatch --wait --dependency=singleton --job-name="${JOBNAME}" completion.slurm -r "${SCRIPTS}" -d "${DB}"
if [ $rc -ne 0 ]; then
    exit $rc
fi

for j in ${jobs[@]}; do
    RUNDIR=/scratch/${USER}/jobs/${JOBNAME}/${j}
    if [ ! -d ${RUNDIR} ]; then
        echo error: could not locate ${RUNDIR}
        exit 1
    fi
    sacct -l -j ${j} --json >> ${RUNDIR}/slurm.json
    $SCRIPTS/sqlutils.py slurm-info --jobpath=${RUNDIR} --jobid=${j} --db=${DB}
    echo "Wrote ${RUNDIR}/slurm.json and updated ${DB}"
done

sqlite3 timing.db << EOF
.tables
.headers on
.echo on

select * from job_info;

select * from file_info;

select * from timing_info;

select * from conf_info;

EOF

echo slurm-check.sh finished
