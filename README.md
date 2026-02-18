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
* *grid* : Generates a configurable 2 dimensional grid network with configurable component and data transfer parameters. Compile options are provided for testing different container data types for evaluating checkpointing performance. 
* *noodle* : Generates randomly connected components using a configurable number of 
ports per component and randomly sends a configurable number of message payloads per cycle.
* *hpe-phold* : Port of PHOLD benchmark from https://github.com/hpc-ai-adv-dev/sst-benchmarks based on Fujimoto's 1990 paper [Performance of Time Warp Under Synthetic Workloads](https://gdo149.llnl.gov/attachments/20776356/24674621.pdf).

## Prerequisites

Given that this is an SST external component, the primary prerequisite is a current installation of the SST Core. Some microbenchmarks use components from SST Elements so it is recommended to install that as well. These test case are labeled 'elements' so they can easily be excluded from testing.  The sst-bench building infrastructure assumes that the `sst-config` tool is installed and can be found in the current PATH environment.

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
If SST Elements is not installed, the dependent tests can be excluded using:
```
ctest -LE elements
```

A special set of long tests that may create extremely large files and can be excluded using:
```
ctest -LE large
```

Currently, the checkpoint tests may generate a large number of files. To clean up after running tests use
```
cd ..
git clean -f -d
```

## Special Runtime Notes

### Benchmark Scale
Be mindful of the simulation input size when scaling tests near the limits of physical memory or compute capacity.  Several benchmarks exhibit exponential memory growth.

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
