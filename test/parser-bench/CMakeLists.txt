#
# sst-bench/test/parser-bench CMake
#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

if(NOT SSTBENCH_ENABLE_TESTING)
  return()
endif()

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(passRegex "Simulation is complete")
set(CONFIG_GEN "${CMAKE_SOURCE_DIR}/scripts/config_generator.py")
set(NDJSON_EMITTER "${CMAKE_SOURCE_DIR}/scripts/emit_ndjson.py")
set(PARITY_GEN "${CMAKE_CURRENT_SOURCE_DIR}/generate_parity_configs.py")
set(GEN_DIR "${CMAKE_CURRENT_BINARY_DIR}/configs")
set(NOODLE_LIB_PATH "${CMAKE_BINARY_DIR}/sst-bench/noodle")

file(MAKE_DIRECTORY ${GEN_DIR})

# --timing-info-json was added in SST 15.1; omit it for older versions
if(SST_MAJOR_VERSION GREATER_EQUAL 15 AND SST_MINOR_VERSION GREATER_EQUAL 1)
  set(HAVE_TIMING_JSON TRUE)
  message(STATUS "[PARSER-BENCH] SST ${SST_MAJOR_VERSION}.${SST_MINOR_VERSION} supports --timing-info-json")
else()
  set(HAVE_TIMING_JSON FALSE)
  message(STATUS "[PARSER-BENCH] SST ${SST_MAJOR_VERSION}.${SST_MINOR_VERSION} lacks --timing-info-json, skipping timing output")
endif()

# ---------------------------------------------------------------------------
# Helper: generate a config and register a test
# ---------------------------------------------------------------------------
function(add_parser_bench_test topology size fmt ports timeout labels)
  set(test_name "parser-bench-${topology}-${size}-${fmt}")

  if(fmt STREQUAL "json")
    set(ext ".json")
  else()
    set(ext ".py")
  endif()

  set(config_file "${GEN_DIR}/${test_name}${ext}")
  set(timing_file "${GEN_DIR}/${test_name}.timing.json")

  # Generate config at configure time
  execute_process(
    COMMAND ${Python3_EXECUTABLE} ${CONFIG_GEN}
      --num-comps ${size}
      --ports-per-comp ${ports}
      --topology ${topology}
      --format ${fmt}
      --clocks 1000
      --rng-seed 31337
      -o ${config_file}
    RESULT_VARIABLE gen_result
  )
  if(NOT gen_result EQUAL 0)
    message(WARNING "[PARSER-BENCH] Failed to generate ${config_file}")
    return()
  endif()

  if(HAVE_TIMING_JSON)
    add_test(NAME ${test_name}
      WORKING_DIRECTORY ${GEN_DIR}
      COMMAND sst --add-lib-path=${NOODLE_LIB_PATH}
        --timing-info-json=${timing_file}
        ${config_file})
  else()
    add_test(NAME ${test_name}
      WORKING_DIRECTORY ${GEN_DIR}
      COMMAND sst --add-lib-path=${NOODLE_LIB_PATH}
        ${config_file})
  endif()

  set_tests_properties(${test_name}
    PROPERTIES
    TIMEOUT ${timeout}
    LABELS "${labels}"
    FIXTURES_SETUP parser_bench_results
    PASS_REGULAR_EXPRESSION "${passRegex}")
endfunction()

# ---------------------------------------------------------------------------
# Topology sweep (chain and fully-connected only)
# ---------------------------------------------------------------------------

# Small tier: 4, 8, 16
foreach(size 4 8 16)
  foreach(topo chain fully-connected)
    foreach(fmt python json)
      if(topo STREQUAL "fully-connected")
        set(ports 4)
      else()
        set(ports 2)
      endif()
      add_parser_bench_test(${topo} ${size} ${fmt} ${ports} 30 "all;parser-bench")
    endforeach()
  endforeach()
endforeach()

# Medium tier: 50, 100
# Note: fully-connected at 100 is promoted to the large tier (600s timeout)
foreach(size 50 100)
  foreach(topo chain fully-connected)
    if("${topo}" STREQUAL "fully-connected" AND "${size}" EQUAL 100)
      continue()
    endif()
    foreach(fmt python json)
      if(topo STREQUAL "fully-connected")
        set(ports 4)
      else()
        set(ports 2)
      endif()
      add_parser_bench_test(${topo} ${size} ${fmt} ${ports} 120 "all;parser-bench;medium")
    endforeach()
  endforeach()
endforeach()

# Large tier: 500, 1000 — chain only
foreach(size 500 1000)
  foreach(fmt python json)
    add_parser_bench_test(chain ${size} ${fmt} 2 600 "parser-bench;large")
  endforeach()
endforeach()

# Large tier: fully-connected capped at 100 nodes (4,950 links)
foreach(fmt python json)
  add_parser_bench_test(fully-connected 100 ${fmt} 4 600 "parser-bench;large")
endforeach()

# ---------------------------------------------------------------------------
# JSON parity tests (noodle-test1/2/3 equivalents)
# ---------------------------------------------------------------------------

execute_process(
  COMMAND ${Python3_EXECUTABLE} ${PARITY_GEN} ${GEN_DIR}
  RESULT_VARIABLE parity_result
)
if(NOT parity_result EQUAL 0)
  message(WARNING "[PARSER-BENCH] Failed to generate parity configs")
endif()

foreach(test_num 1 2 3)
  set(test_name "parser-bench-noodle-test${test_num}-json")
  set(config_file "${GEN_DIR}/noodle-test${test_num}.json")
  set(timing_file "${GEN_DIR}/${test_name}.timing.json")

  if(HAVE_TIMING_JSON)
    add_test(NAME ${test_name}
      WORKING_DIRECTORY ${GEN_DIR}
      COMMAND sst --add-lib-path=${NOODLE_LIB_PATH}
        --timing-info-json=${timing_file}
        ${config_file})
  else()
    add_test(NAME ${test_name}
      WORKING_DIRECTORY ${GEN_DIR}
      COMMAND sst --add-lib-path=${NOODLE_LIB_PATH}
        ${config_file})
  endif()

  set_tests_properties(${test_name}
    PROPERTIES
    TIMEOUT 30
    LABELS "all;parser-bench"
    FIXTURES_SETUP parser_bench_results
    PASS_REGULAR_EXPRESSION "${passRegex}")
endforeach()

# ---------------------------------------------------------------------------
# NDJSON emitter — print results to console after the test suite
# ---------------------------------------------------------------------------
# CTest's --output-on-failure hides stdout from passing tests, so we use
# CTEST_CUSTOM_POST_TEST to run the emitter *after* the test suite.  Its
# output goes directly to the console (visible in Jenkins for Logstash).
file(WRITE "${CMAKE_BINARY_DIR}/CTestCustom.cmake"
  "set(CTEST_CUSTOM_POST_TEST \"${Python3_EXECUTABLE} -u ${NDJSON_EMITTER} --timing-dir ${GEN_DIR}\")\n")

# EOF
