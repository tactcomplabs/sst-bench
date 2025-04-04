#!/bin/bash

export SST_GRID_SDL=$(realpath ../2d.py)

printf "Submitting base simulation\n"
id_base=$(sbatch --parsable -N 1 -n 1 -J CHECK grid.slurm  -- --verbose=1 --x=2 --y=1 --clocks=10000)
rc=$?
if [ $rc -ne 0 ]; then
	exit $rc
fi
printf "Job submitted with ID: $id_base\n\n"

printf "Submitting checkpoint simulation\n"
id_cpt=$(sbatch --parsable -N 1 -n 1 -J CHECK grid.slurm  --checkpoint-prefix=_cpt --checkpoint-sim-period=1000ns --checkpoint-name-format=%n_%t/grid -- --verbose=1 --x=2 --y=1 --clocks=10000)
rc=$?
if [ $rc -ne 0 ]; then
	exit $rc
fi
printf "Job submitted with ID: $id_cpt\n\n"

printf "Submitting dependent restart simulations\n"
declare -a ids=("1_1" "2_2" "3_3" "4_4" "5_5" "6_6" "7_7" "8_8" "9_9" "10_10")
for id in "${ids[@]}"; do
    id_rst=$(sbatch --dependency=afterok:${id_cpt} --parsable -N 1 -n 1 -J CHECK grid.slurm --load-checkpoint ../${id_cpt}/_cpt/${id}000000/grid.sstcpt)
    rc=$?
    if [ $rc -ne 0 ]; then
        exit $rc
    fi
    printf "Job submitted with ID: $id_rst\n\n"
done

echo slurm-check.sh finished
