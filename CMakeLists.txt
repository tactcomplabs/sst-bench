#
# sst-bench top-level CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

# ---------------------------------------------------
# string_contains_number
# ---------------------------------------------------
function(string_contains_number str result)
  string(REGEX MATCH "[0-9]" has_number "${str}")
  if(has_number)
    set(${result} TRUE PARENT_SCOPE)
  else()
    set(${result} FALSE PARENT_SCOPE)
  endif()
endfunction()

# ---------------------------------------------------
# main
# ---------------------------------------------------
#-- Prevent in-source builds
if(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
  message(FATAL_ERROR "DO NOT BUILD in-tree.")
endif()

# Minimum required version of CMake and project information
cmake_minimum_required(VERSION 3.19)
project(sst-bench CXX)
message(STATUS "CMAKE_BINARY_DIR = ${CMAKE_BINARY_DIR}")

# Local scripts
set(SCRIPTS "${CMAKE_CURRENT_SOURCE_DIR}/scripts")

# SST Configuration Sanity Check
find_program(SST sst)
find_program(SST_CONFIG sst-config)
if(NOT SST OR NOT SST_CONFIG)
  message(FATAL_ERROR "No SST binary or sst-config binary found in path")
endif()

# SST Environment Derivation
execute_process(COMMAND sst-config --prefix
                OUTPUT_VARIABLE SST_INSTALL_DIR
                OUTPUT_STRIP_TRAILING_WHITESPACE
)
set(SST_INCLUDE_DIR "${SST_INSTALL_DIR}/include")
if(NOT (EXISTS "${SST_INSTALL_DIR}"))
  message(FATAL_ERROR " SST_INSTALL_DIR (${SST_INSTALL_DIR}) is invalid.")
endif()
include_directories(${SST_INSTALL_DIR})

# SST Version found in path
execute_process(COMMAND sst --version
                OUTPUT_VARIABLE SST_VERSION_STRING
                OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "${SST_VERSION_STRING}")

# SST Flags
execute_process(COMMAND sst-config --CXX
                OUTPUT_VARIABLE CXX
                OUTPUT_STRIP_TRAILING_WHITESPACE
)
execute_process(COMMAND sst-config --ELEMENT_CXXFLAGS
                OUTPUT_VARIABLE SST_CXXFLAGS
                OUTPUT_STRIP_TRAILING_WHITESPACE
)
set(CXXFLAGS "${SST_CXXFLAGS}  -fno-stack-protector")
execute_process(COMMAND sst-config --ELEMENT_LDFLAGS
                OUTPUT_VARIABLE SST_LDFLAGS
                OUTPUT_STRIP_TRAILING_WHITESPACE
)
set(LDFLAGS "${SST_LDFLAGS}  -fno-stack-protector")

execute_process(COMMAND sst-config SST_ELEMENT_LIBRARY SST_ELEMENT_LIBRARY_LIBDIR
                OUTPUT_VARIABLE SST_ELEMENT_LIBRARY_LIBDIR
                OUTPUT_STRIP_TRAILING_WHITESPACE
)

# Underscore prefix convention indicates private scope.
# Use the resolved SST_VERSION in other other cmake files
execute_process(COMMAND ${SCRIPTS}/sst-major-version.sh
                OUTPUT_VARIABLE _SST_MAJOR_VERSION
                OUTPUT_STRIP_TRAILING_WHITESPACE
)
execute_process(COMMAND ${SCRIPTS}/sst-minor-version.sh
                OUTPUT_VARIABLE _SST_MINOR_VERSION
                OUTPUT_STRIP_TRAILING_WHITESPACE
)

string_contains_number("${_SST_MAJOR_VERSION}" contains_num)
if(NOT contains_num)
  set(_SST_MAJOR_VERSION "DEV")
  set(_SST_MINOR_VERSION "DEV")
  execute_process(COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/scripts/sst-git-hash.sh
                  OUTPUT_VARIABLE SST_GIT_HASH
                  OUTPUT_STRIP_TRAILING_WHITESPACE
  )
  message(STATUS "SST GIT HASH=${SST_GIT_HASH}")
endif()

#-- Create version variables (will rewrite command line provided SST_VERSION)
message(STATUS "SST MAJOR VERSION=${_SST_MAJOR_VERSION}")
message(STATUS "SST MINOR VERSION=${_SST_MINOR_VERSION}")

# Allow override using -DSST_VERSION=n
# Important: subdirectories should only use this resolved version
if (DEFINED SST_VERSION)
  message(STATUS "SST_VERSION test selection override: ${SST_VERSION}")
elseif ("${_SST_MAJOR_VERSION}" STREQUAL "DEV")
  set(SST_VERSION "DEV")
else()
 string(CONCAT SST_VERSION  ${_SST_MAJOR_VERSION} "." ${_SST_MINOR_VERSION})
endif()
message(STATUS "RESOLVED SST VERSION=${SST_VERSION}")


#-- MPI Options
find_package(MPI)
if(MPIEXEC_EXECUTABLE)
  message(STATUS "MPI RUN COMMAND=${MPIEXEC_EXECUTABLE}")
endif()

#-- setup the component build directory
set(ENV{SST_COMPONENT_BASE} "${CMAKE_BINARY_DIR}/components")
message(STATUS "SST-EXT-TESTS ENV{SST_COMPONENT_BASE}=$ENV{SST_COMPONENT_BASE}")

#-- Compiler Options
option(SST_WERROR "Compile with warnings as errors" ON)
if (SST_WERROR)
  set(WERROR_FLAG "-Werror")
endif()

option(SST_ASAN "Compile using address sanitizer" OFF)
if (SST_ASAN)
  set (SANITIZE_FLAG "-fsanitize=address -fno-omit-frame-pointer")
endif()

#set(SST_SUGGEST_FINAL -Wsuggest-final-methods -Wsuggest-final-types")

# Compiler Options
if ("${CMAKE_CXX_COMPILER_ID}" MATCHES "Clang")
  set(FP_MODE_FLAG "-ffp-model=strict -frounding-math -ftrapping-math")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-unused-command-line-argument")
else()
  set(FP_MODE_FLAG "-frounding-math -ftrapping-math")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wmissing-format-attribute -Wvolatile ${SST_SUGGEST_FINAL}")
endif()

set(CMAKE_CXX_FLAGS "-std=c++17 ${FP_MODE_FLAG} -O2 -Wall -Wextra -Wsuggest-override -Wmissing-noreturn -Wvla -Wuninitialized -Wfloat-conversion -Wdouble-promotion -Wsign-conversion -Wconversion -Wno-unused-parameter -Wno-deprecated-declarations -Wno-macro-redefined ${WERROR_FLAG} ${SANITIZE_FLAG} ${CMAKE_CXX_FLAGS} -I./ ${LDFLAGS}")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -O0 -Wall")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -Wall")

#---------------------------------------------
# TARGET OPTIONS
#---------------------------------------------

#-- Benchmark Options
#TODO replace these with interactive console micro-benchmarks
# option(SSTBENCH_ENABLE_SSTDBG "Enable SST-DBG Benchmarks" OFF)
# if(SSTBENCH_ENABLE_SSTDBG)
#   set(ENABLE_SSTDBG "ON")
# endif()

# ---------------------------------------------------
# add_perf_sweep(<test_name> <sdl_file> <sweep_name> <tier>
#                [TIMEOUT <seconds>])
#
# Registers a CTest that invokes scripts/sst-sweeper.py with --seq=BASE
# and the named sweep entry from the benchmark's sweep.json. The test is
# labeled perf-<tier> so Jenkins can filter via `ctest -L perf-<tier>`.
# The sweeper emits ###SST_BENCH_PERF_V1###...###END### markers to stdout;
# PASS_REGULAR_EXPRESSION fails the test if no marker is emitted.
#
# SST_BENCH_RUN_ID baked into the test env uses $ENV{BUILD_TAG} captured
# at configure time; Jenkins re-configures per build so the run_id is
# unique per (build, bench, tier). Local devs get a deterministic id.
# ---------------------------------------------------
function(add_perf_sweep testName sdl sweep tier)
  cmake_parse_arguments(APS "" "TIMEOUT" "" ${ARGN})
  if(NOT APS_TIMEOUT)
    if("${tier}" STREQUAL "fast")
      set(APS_TIMEOUT 180)
    elseif("${tier}" STREQUAL "medium")
      set(APS_TIMEOUT 900)
    else()
      set(APS_TIMEOUT 3600)
    endif()
  endif()
  add_test(NAME ${testName}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMAND ${SCRIPTS}/sst-sweeper.py
            ${CMAKE_CURRENT_SOURCE_DIR}/sweep.json
            ${CMAKE_CURRENT_SOURCE_DIR}/${sdl}
            ${sweep}
            --tmpdir ${CMAKE_CURRENT_SOURCE_DIR}/run
            --jobname=${testName}
            --seq=BASE
            --noprompt)
  set_tests_properties(${testName} PROPERTIES
    TIMEOUT ${APS_TIMEOUT}
    LABELS "perf-${tier}"
    PASS_REGULAR_EXPRESSION "###SST_BENCH_PERF_V1###"
    ENVIRONMENT "SST_BENCH_RUN_ID=$ENV{BUILD_TAG}-${testName};SST_BENCH_HOME=${CMAKE_SOURCE_DIR}")
endfunction()

#-- Testing Options
option(SSTBENCH_ENABLE_TESTING "Enable Testing" OFF)
if(SSTBENCH_ENABLE_TESTING)
  enable_testing()
  add_subdirectory(test)
endif()

#-- Custom Commands
add_custom_target(uninstall COMMAND
  "${CMAKE_CURRENT_SOURCE_DIR}/scripts/uninstall.sh")

#-- Subdirectories
add_subdirectory(components)

# EOF
