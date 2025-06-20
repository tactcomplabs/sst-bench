# SST-Bench Examples

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

Finally, clean and rebuild `sst-bench` using this version of SST following the instructions in the top level README.md.

## System Requirements

These examples demonstrate scripts that support simulation job management and performance data capture for systems supporting MPI with or without Slurm support. That is, if Slurm support is not available, a built-in job manager is provided that allows launching and monitoring parameter sweep simulations.

These scripts have been tested on the following Operating Systems:

- Linux 6.8.0-60-generic #63-Ubuntu SMP PREEMPT_DYNAMIC Tue Apr 15 19:04:15 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux

- Linux 4.18.0-477.10.1.el8_8.x86_64 #1 SMP Tue May 16 11:38:37 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux

- Darwin 24.5.0 Darwin Kernel Version 24.5.0: Tue Apr 22 19:54:25 PDT 2025; root:xnu-11417.121.6~2/RELEASE_ARM64_T6020 arm64

## Overview

TODO
- example charts
- flow diagram
- directory structure

## Running MPI-only Simulations




