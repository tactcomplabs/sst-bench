#!/bin/bash

mpirun -np 2 sst ${SST_BENCH_HOME}/benchmarks/noodle/noodle-bench.py --num-threads=1 --output-config=config.py --parallel-output --add-lib-path=${SST_BENCH_HOME}/sst-bench/build/components/noodle -- --verbose=0 --numComps=1000 --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=100 --rngSeed=3131

mpirun -np 2 sst  --num-threads=1 --add-lib-path=${SST_BENCH_HOME}/build/components/noodle --parallel-load ./config.py
