#!/bin/bash -x
sst --version
mpirun --version
uname -v 

OPTS="--parallel-output=1 --verbose=4 --print-timing-info=4 -- --numComps=100 --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=1000 --rngSeed=3131"

# echo "### 3 threads: no mpi"
# sst ../noodle-bench.py --num-threads=3 --output-config=t3-nompi.py ${OPTS}
# sst t3-nompi.py --parallel-load --num-threads=3

# echo "### 3 threads: with mpi"
# mpirun -np 1 sst ../noodle-bench.py --num-threads=3 --output-config=t3-mpi.py ${OPTS}
# mpirun -np 1 sst t3-mpi.py --parallel-load --num-threads=3

# echo "### 2 ranks"
# mpirun -np 2 sst ../noodle-bench.py --output-config=r2.py  ${OPTS}
# mpirun -np 2 sst r2.py --parallel-load
# wait

echo "### 3 ranks"
mpirun -np 3 sst ../noodle-bench.py --output-config=r3.py  ${OPTS}
wait
mpirun -np 3 sst r3.py --parallel-load
wait