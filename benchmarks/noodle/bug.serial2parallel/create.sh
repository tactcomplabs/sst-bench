#!/bin/bash

mpirun -np 2 sst /Users/kgriesser/work/sst-bench/benchmarks/noodle/noodle-bench.py --output-config=config.py --add-lib-path=/Users/kgriesser/work/sst-bench/build/components/noodle -- --verbose=0 --numComps=1000 --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=100 --rngSeed=3131


