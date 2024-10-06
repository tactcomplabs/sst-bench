#
# sst-bench/test/chkpnt CMake
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

file(GLOB CHKPNT_TEST_SRCS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} *.py)

if(SSTBENCH_ENABLE_TESTING)
  set (passRegex "Simulation is complete")

  foreach(testSrc ${CHKPNT_TEST_SRCS})
    get_filename_component(testName ${testSrc} NAME_WE)
    if(NOT ${testName} MATCHES "checkpoint_dump")
      add_test(NAME ${testName}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMAND ${SCRIPTS}/sst-chkpt.sh ${testName}_SAVE_ --checkpoint-period=10ns --add-lib-path=${CMAKE_BINARY_DIR}/sst-bench/chkpnt ${testSrc})
      set_tests_properties(${testName}
        PROPERTIES
        TIMEOUT 60
        LABELS "all"
        PASS_REGULAR_EXPRESSION "${passRegex}")
      endif()
  endforeach(testSrc)
endif()

# EOF
