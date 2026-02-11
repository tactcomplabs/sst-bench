#
# sst-bench/test/hpe-phold CMake
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

file(GLOB PHOLD_TEST_SOURCES RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} phold_dist.py)

set(SST_OPTS --parallel-load=SINGLE)
set(SDL_OPTS --height 100 --width 100 --eventDensity 2.0 --timeToRun 100ns --numRings 2 --smallPayload 8 --largePayload 1024 --largeEventFraction 0.0 --imbalance-factor 0.0 --componentSize 0)

if(SSTBENCH_ENABLE_TESTING)
  set (passRegex "Simulation is complete")
  foreach(testSrc ${PHOLD_TEST_SOURCES})
    get_filename_component(testName ${testSrc} NAME_WE)
    set(CHKPT_PFX ${testName}_SAVE_)
    add_test(NAME ${testName}_SAVE
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      COMMAND ${SCRIPTS}/sst-chkpt.sh ${CHKPT_PFX} --checkpoint-period=10ns --add-lib-path=${CMAKE_BINARY_DIR}/sst-bench/hpe-phold ${SST_OPTS} ${testSrc} -- ${SDL_OPTS})
    set_tests_properties(${testName}_SAVE
      PROPERTIES
      TIMEOUT 60
      LABELS "all"
      PASS_REGULAR_EXPRESSION "${passRegex}")
    add_test(NAME ${testName}_RESTORE
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      COMMAND sst --add-lib-path=${CMAKE_BINARY_DIR}/sst-bench/hpe-phold --load-checkpoint ${CHKPT_PFX}/${CHKPT_PFX}_5_50000/${CHKPT_PFX}_5_50000.sstcpt)
    set_tests_properties(${testName}_RESTORE
      PROPERTIES
      TIMEOUT 60
      LABELS "all"
      DEPENDS ${testName}_SAVE
      PASS_REGULAR_EXPRESSION "${passRegex}")
  endforeach(testSrc)
endif()

# EOF
