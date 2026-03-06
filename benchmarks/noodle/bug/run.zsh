#!/bin/zsh -x
sst --version
mpirun --version
uname -v 

OPTS="--verbose=4 --print-timing-info=4 --parallel-output -- --numComps=100 --portsPerComp=100 --msgPerClock=8 --bytesPerClock=4 --clocks=1000 --rngSeed=3131"

# echo "### 3 threads: no mpi"
# sst ../noodle-bench.py --num-threads=3 --output-config=t3-nompi.py $OPTS
# sst t3-nompi.py --parallel-load --num-threads=3

# echo "### 3 threads: with mpi"
# mpirun -np 3 sst ../noodle-bench.py --output-config=t3-mpi.py $OPTS
# mpirun -np 3 sst t3-mpi.py --parallel-load

# echo "### 2 ranks"
# mpirun -np 2 sst ../noodle-bench.py --output-config=r2.py --parallel-output $OPTS
# mpirun -np 2 sst r2.py --parallel-load

echo "### 3 ranks"
mpirun -np 3 sst ../noodle-bench.py --output-config=r3.py --parallel-output $OPTS
wait
mpirun -np 3 sst r3.py --parallel-load
wait
