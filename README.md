# sst-bench

## Getting Started

The *sst-bench* infrastructure contains a set of specifically crafted 
SST components, subcomponents, links and associated APIs designed to 
exercise specific aspects of the Structural Simulation Toolkit.  The current 
set of benchmarks includes:

* *msg-perf* : Tests the performance of sending incrementally sized messages 
over `simpleNetwork` links in a ring-network pattern.
* *micro-comp* : Tests the performance of loading a large number of small components 
using the various loading methodologies
* *micro-comp-link* : Similar to `micro-comp` but adds in link configuration with 
a single link per component that utilizes SimpleNetwork.  Tests the loading 
of large numbers of components with the default SST partitioner.
* *chkpnt* : Tests the performance of the checkpoint/restart functionality 
present in SST-14.0.0+.  Note that this test is currently only built when SST 
14.0.0 is detected and can be only run in sequential execution mode.  Threading 
and MPI are not currently supported for checkpoint/restart in SST 14.0.0.
* *restore* : Tests the storing and loading of well-defined simulation component data using 
the SST 14.0.0 checkpoint/restart functionality
* *restart* : Sanity checks data after a context restore operation using the 
SST 14.0.0 checkpoint/restart functionality
* *large-stat* : Tests the creation of instantiation of a variable number of unsigned 
64bit statistics for very simple components.  Designed to test large blocks of 
statistics values for simple components.
* *grid* : Generates a configurable 2 dimensional grid network with configurable component and data transfer parameters. Designed to profile simulation performance by sweeping component counts, data sizes, and thread counts.

## Prerequisites

Given that this is an SST external component, the primary prerequisite is a
current installation of the SST Core. The Rev building infrastructure assumes
that the `sst-config` tool is installed and can be found in the current PATH
environment.

*sst-bench* relies upon CMake for building the component source.  The minimum 
required version for this is `3.19`

## Building

Building the *sst-bench* infrastructure from source can be performed 
using the following steps:

```
git clone https://github.com/tactcomplabs/sst-bench.git
cd sst-bench
mkdir build
cd build
cmake ../
make && make install
```

Additional build options include:
* `make uninstall` : forcible uninstalls the included components/subcomponents 
from the current version of SST
* `cmake -DSSTBENCH_ENABLE_TESTING=ON ../` : Enables included test harness: 
run with `make test`
* `cmake -DSSTBENCH_ENABLE_SSTDBG=ON ../` : Enables TCL SST-Dbg components

## Testing

Utilize the included test harness to test and ensure all tests are passing 
before opening new pull requests.  The test harness can be enabled when 
you run the CMake configuration step as follows:

```
cmake -DSSTBENCH_ENABLE_TESTING=ON ../
make -j
make install
make test
```

A special set of long tests that may create extremely large files can be excluded using:
```
ctest -E large
```

## Special Runtime Notes

### TCL-DBG Benchmark

The `tcl-dbg` micro benchmark is designed to test the report the cost of using 
the TactCompLabs `sst-dbg` tool flow using a variety of data sizes.  The benchmark 
randomly seeds a randomly sized `std::vector` container at a specified interval.  Users 
can then utilize `sst-dbg` or the `sst-dbg-console` application to trigger debugging 
outputs at a specified interval.  The timing reported is *only* the time required to output 
the debug data to disk.  An example of executing this benchmark is as follows:

```
cd sst-bench/test/tcl-dbg
sst-dbg -i 1 -- sst tcldbg-test1.py
```

The timing data and size of the vectors (in bytes) will be written to an SST Statistics 
file (StatisticOutput.csv) using the histogram output format.

## Contributing

We welcome outside contributions from corporate, academic and individual
developers. However, there are a number of fundamental ground rules that you
must adhere to in order to participate. These rules are outlined as follows:

* By contributing to this code, one must agree to the licensing described in
the top-level [LICENSE](LICENSE) file.
* All code must adhere to the existing C++ coding style. While we are somewhat
flexible in basic style, you will adhere to what is currently in place. This
includes camel case C++ methods and inline comments. Uncommented, complicated
algorithmic constructs will be rejected.
* We support compilaton and adherence to C++ standard methods. All new methods
and variables contained within public, private and protected class methods must
be commented using the existing Doxygen-style formatting. All new classes must
also include Doxygen blocks in the new header files. Any pull requests that
lack these features will be rejected.
* All changes to functionality and the API infrastructure must be accompanied
by complementary tests All external pull requests **must** target the `devel`
branch. No external pull requests will be accepted to the master branch.
* All external pull requests must contain sufficient documentation in the pull
request comments in order to be accepted.

## License

See the [LICENSE](./LICENSE) file

## Authors
* John Leidel
* Ken Griesser
* Shannon Kuntz
