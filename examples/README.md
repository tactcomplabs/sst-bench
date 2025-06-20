# SST-Bench Examples

## Overview

TODO
- example charts
- flow diagram
- directory structure

## SST Requirements
Currently, these examples require a custom branch of `sst-core` to provide simulation timing data in JSON format. This feature is expected to be available in SST v15.1.0. 

Installing `sst-core/v15.0.0.tcl` from TCL's github:
```
git clone https://github.com/tactcomplabs/sst-core
cd sst-core
git checkout v15.0.0.tcl
./autogen.sh
mkdir build && cd build
../configure --prefix=<sst-install-dir>
make -j -s && make install
```

Be sure to update your `PATH` environment variable to include `<sst-install-dir>/bin`.

Installation of sst-elements is optional. If it is installed be sure to use the compatable `v15.0.0_beta` branch.

Finally, clean and rebuild `sst-bench` using this version of SST following the instructions in the top level README.md.
To test sst-bench without sst-elements installed use `ctest -LE elements`

## System Requirements

These examples demonstrate scripts that support simulation job management and performance data capture for systems supporting MPI with or without Slurm support. That is, if Slurm support is not available, a built-in job manager is provided that allows launching and monitoring parameter sweep simulations.

These scripts have been tested on the following Operating Systems:

- Linux 6.8.0-60-generic #63-Ubuntu SMP PREEMPT_DYNAMIC Tue Apr 15 19:04:15 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux

- Linux 4.18.0-477.10.1.el8_8.x86_64 #1 SMP Tue May 16 11:38:37 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux

- Darwin 24.5.0 Darwin Kernel Version 24.5.0: Tue Apr 22 19:54:25 PDT 2025; root:xnu-11417.121.6~2/RELEASE_ARM64_T6020 arm64

## Environment Variables

The following environment variable is required:

```
export SST_BENCH_HOME=<path-to-sstbench>
```

## Running Simulations: General tips

If you are running on a system using Slurm job management you can still run MPI simulations interactively. Be sure to allocate the necessary compute resource using `salloc -N <nodes> -n <processors>`

Generally, the scripts should be run on a fast local disk rather than on NFS as disk latencies have a major impact on performance. This is especially true when running with checkpointing and restarting from checkpoints which have high disk usage.

For example, if there exist a local disk `/scratch/$USER`, copy the example directory to that disk and run the scripts from there. e.g.

```
export SST_BENCH_HOME=<path-to-sst-bench>
# salloc is optional depending on the host platform policy
salloc -N 1 -n 40  
cd /scratch/$USER
mkdir sst-bench-data && cd sst-bench-data
mkdir run1 && cd run1
cp $SST_BENCH_HOME/examples/comp-size.sh
# Modify the local copy of the script to customize behaviors
./comp-size.sh 
```

## Example: comp-size.sh

Setup:

```
# components        10                          # Number of components
# link_delay        10000,11000 (random)        # Delay between link transmissions
# clocks            10000                       # Number of clocks to simulate
# cpt-sim-period     5000                       # Number of clocks between checkpoints

# Parameter sweep variables set with sst_perfdb command line
# srange    1000 to 11000 step 5000     # Number of state elements per component
# rrange    2 to 8 step 2               # Sweep of ranks
```

To run:
```
$ ./comp-size.sh
```

The jobs will be run serially to permute the component state size and number of ranks. Each job will be run without checkpointing, with checkpointing enabled, and restarting from each checkpoint.

Results:
```
$ ls
alldata.csv  basecpt.csv  base.csv  comp-size-mpi/  comp-size.sh*  cpt.csv  cptrst.csv  host.info  rst.csv  timing.db
```

```
$ tree comp-size-mpi 
comp-size-mpi
├── 381208231936
│   ├── config.json
│   ├── log
│   └── timing.json
├── 381208231937
│   ├── config.json
│   ├── _cpt
│   │   ├── 1_5000000
│   │   │   ├── grid_0_0.bin
│   │   │   ├── grid_1_0.bin
│   │   │   ├── grid_globals.bin
│   │   │   └── grid.sstcpt
│   │   └── 2_10000000
│   │       ├── grid_0_0.bin
│   │       ├── grid_1_0.bin
│   │       ├── grid_globals.bin
│   │       └── grid.sstcpt
│   ├── log
│   └── timing.json
├── 381208231938
│   ├── log
│   └── timing.json
├── 381208231939
│   ├── log
│   └── timing.json
├── 381208231940
│   ├── config.json
│   ├── log
│   └── timing.json
├── 381208231941
│   ├── config.json
│   ├── _cpt
│   │   ├── 1_5000000
│   │   │   ├── grid_0_0.bin
│   │   │   ├── grid_1_0.bin
│   │   │   ├── grid_2_0.bin
│   │   │   ├── grid_3_0.bin
│   │   │   ├── grid_globals.bin
│   │   │   └── grid.sstcpt
│   │   └── 2_10000000
│   │       ├── grid_0_0.bin
│   │       ├── grid_1_0.bin
│   │       ├── grid_2_0.bin
│   │       ├── grid_3_0.bin
│   │       ├── grid_globals.bin
│   │       └── grid.sstcpt
│   ├── log
│   └── timing.json
| ... etc...
```


