#
# sst-bench/test/msg-perf CMake
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

file(GLOB MSGPERF_TEST_SRCS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} *.py)

if(SSTBENCH_ENABLE_TESTING)
  set (passRegex "Simulation is complete")

  foreach(testSrc ${MSGPERF_TEST_SRCS})
    get_filename_component(testName ${testSrc} NAME_WE)
    add_test(NAME ${testName}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      COMMAND sst --add-lib-path=${CMAKE_BINARY_DIR}/sst-bench/msg-perf/ ${testSrc})
    set_tests_properties(${testName}
      PROPERTIES
      TIMEOUT 30
      LABELS "all"
      PASS_REGULAR_EXPRESSION "${passRegex}")
  endforeach(testSrc)
endif()

# EOF
