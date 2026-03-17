#!/bin/bash

echo checking serial load
mpirun -np 2 sst --add-lib-path=/Users/kgriesser/work/sst-bench/build/components/noodle ./config.py

echo generating parallel output from serial output
mpirun -np 2 sst --parallel-output --output-config=pconfig.py --add-lib-path=/Users/kgriesser/work/sst-bench/build/components/noodle ./config.py

# for comparison with bug.parallel/sorted.py
sort pconfig*.py > sorted.py

echo checking parallel load
mpirun -np 2 sst --add-lib-path=/Users/kgriesser/work/sst-bench/build/components/noodle --parallel-load ./pconfig.py


