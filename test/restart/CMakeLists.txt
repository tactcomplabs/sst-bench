#
# sst-bench/test/restart CMake
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

file(GLOB RESTART_TEST_SRCS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} *.py)

if(SSTBENCH_ENABLE_TESTING)
  set (passRegex "Simulation is complete")

  foreach(testSrc ${RESTART_TEST_SRCS})
    get_filename_component(testName ${testSrc} NAME_WE)
    add_test(NAME ${testName}_SAVE
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      COMMAND sst --checkpoint-period=5us --checkpoint-prefix=${testName}_SAVE_ --add-lib-path=${CMAKE_BINARY_DIR}/sst-bench/restore ${testSrc})
    set_tests_properties(${testName}_SAVE
      PROPERTIES
      TIMEOUT 60
      LABELS "all"
      PASS_REGULAR_EXPRESSION "${passRegex}")
    add_test(NAME ${testName}_RESTORE
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      COMMAND sst --add-lib-path=${CMAKE_BINARY_DIR}/sst-bench/restore --load-checkpoint ${testName}_SAVE__5000000_0.sstcpt)
    set_tests_properties(${testName}_RESTORE
      PROPERTIES
      TIMEOUT 60
      LABELS "all"
      DEPENDS ${testName}_SAVE
      PASS_REGULAR_EXPRESSION "${passRegex}")
  endforeach(testSrc)
endif()

# EOF
