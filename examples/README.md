# SST-Bench Examples

## Overview

TODO
- example charts
- flow diagram
- directory structure

## System Requirements

These examples demonstrate scripts that support simulation job management and performance data capture for systems supporting MPI with or without Slurm support. That is, if Slurm support is not available, a built-in job manager is provided that allows launching and monitoring parameter sweep simulations.

These scripts have been tested on the following Operating Systems:

- Linux 6.8.0-60-generic #63-Ubuntu SMP PREEMPT_DYNAMIC Tue Apr 15 19:04:15 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux

- Linux 4.18.0-477.10.1.el8_8.x86_64 #1 SMP Tue May 16 11:38:37 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux

- Darwin 24.5.0 Darwin Kernel Version 24.5.0: Tue Apr 22 19:54:25 PDT 2025; root:xnu-11417.121.6~2/RELEASE_ARM64_T6020 arm64


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

When using the slurm job manager, the scripts currently require support for the `sacct` command. This may be an issue for some users so the scripts will be modified to detect the presence of this command before attempting to collect these statistics.

## Example 1: comp-size.sh (interactive)

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
├── 381208231936      # baseline simulation without checkpointing
│   ├── config.json
│   ├── log
│   └── timing.json
├── 381208231937      # simulation with checkpointing
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
├── 381208231938     # simulations restarting from checkpoint
│   ├── log
│   └── timing.json
├── 381208231939     # next simulation restarting from checkpoint
│   ├── log
│   └── timing.json
├── 381208231940     # Next baseline simulation
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

## Example 2: comp-size.sh (slurm)

Create another run directory and copy the same script as Example 1.
This is run from the management node so no need to perform `salloc`.

```
mkdir run2 && cd run2
cp $SST_BENCH_HOME/examples/comp-size.sh .
```

Edit `comp-size.sh` to uncomment the SLURM variable

```
# Uncomment to use slurm job scripts                                                       
SLURM="--slurm"
```

Launch the script
```
./comp-size.sh
```

This will run the same jobs as in example 1 but using `sbatch` commands instead of `mpirun` commands.

Results:
```
$ ls 
alldata.csv     rst.csv          slurm-46372.out  slurm-46381.out  slurm-46390.out  slurm-46399.out
basecpt.csv     slurm-46364.out  slurm-46373.out  slurm-46382.out  slurm-46391.out  slurm-46400.out
base.csv        slurm-46365.out  slurm-46374.out  slurm-46383.out  slurm-46392.out  slurm-46401.out
comp-size-mpi/  slurm-46366.out  slurm-46375.out  slurm-46384.out  slurm-46393.out  slurm-46402.out
comp-size.sh*   slurm-46367.out  slurm-46376.out  slurm-46385.out  slurm-46394.out  slurm-46403.out
cpt.csv         slurm-46368.out  slurm-46377.out  slurm-46386.out  slurm-46395.out  timing.db
cptrst.csv      slurm-46369.out  slurm-46378.out  slurm-46387.out  slurm-46396.out
host.info       slurm-46370.out  slurm-46379.out  slurm-46388.out  slurm-46397.out
log             slurm-46371.out  slurm-46380.out  slurm-46389.out  slurm-46398.out
```

```
$ tree comp-size-mpi
comp-size-mpi
├── 46364                             # baseline simulation
│   ├── config.json
│   ├── log
│   ├── slurm.json
│   └── timing.json
├── 46365                             # simulation with checkpointing
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
│   ├── slurm.json
│   └── timing.json
├── 46366                             # restart from checkpoint
│   ├── log
│   ├── slurm.json
│   └── timing.json
├── 46367                             # restart from checkpoint
│   ├── log
│   ├── slurm.json
│   └── timing.json
├── 46369                             # completion job to read slurm statistics using sacct command
│   ├── config.json
│   ├── log
│   ├── slurm.json
│   └── timing.json
├── 46370                             # the next baseline simulation
```

## Known issues

- When using slurm the `sacct` command must be available so slurm job statistics can be gathered. This will be optional in a future release