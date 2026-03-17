#!/bin/bash

mpirun -np 2 sst  --num-threads=1 --add-lib-path=/Users/kgriesser/work/sst-bench/build/components/noodle --parallel-load ./config.py

