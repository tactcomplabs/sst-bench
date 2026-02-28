#!/bin/bash

export SLURM_CPU_BIND=verbose
CLOCKS=300000

RANKS=8
THREADS=1

sbatch --parsable --wait  -N 1 -n $RANKS -J noodle_perf /scratch/kgriesser/work/sst-bench/scripts/perf.slurm -r /scratch/kgriesser/work/sst-bench/scripts -d /scratch/kgriesser/work/sst-bench/benchmarks/noodle/noodle.db -R /scratch/kgriesser/work/sst-bench/benchmarks/noodle sst /scratch/kgriesser/work/sst-bench/benchmarks/noodle/noodle-bench.py --num-threads=$THREADS --output-json=config.json --print-timing-info --timing-info-json=timing.json --add-lib-path=/scratch/kgriesser/work/sst-bench/components/noodle -- --verbose=0 --numComps=100 --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=$CLOCKS --rngSeed=3131


RANKS=1
THREADS=8

sbatch --parsable --wait  -N 1 -n $RANKS -J noodle_perf /scratch/kgriesser/work/sst-bench/scripts/perf.slurm -r /scratch/kgriesser/work/sst-bench/scripts -d /scratch/kgriesser/work/sst-bench/benchmarks/noodle/noodle.db -R /scratch/kgriesser/work/sst-bench/benchmarks/noodle sst /scratch/kgriesser/work/sst-bench/benchmarks/noodle/noodle-bench.py --num-threads=$THREADS --output-json=config.json --print-timing-info --timing-info-json=timing.json --add-lib-path=/scratch/kgriesser/work/sst-bench/components/noodle -- --verbose=0 --numComps=100 --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=$CLOCKS --rngSeed=3131
