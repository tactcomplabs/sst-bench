#
# sst-bench/test/noodle CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

file(GLOB NOODLE_TEST_SRCS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} *.py)

if(SSTBENCH_ENABLE_TESTING)
  set (passRegex "Simulation is complete")

  foreach(testSrc ${NOODLE_TEST_SRCS})
    get_filename_component(testName ${testSrc} NAME_WE)
    add_test(NAME ${testName}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      COMMAND sst --add-lib-path=${CMAKE_BINARY_DIR}/sst-bench/noodle ${testSrc})
    set_tests_properties(${testName}
      PROPERTIES
      TIMEOUT 30
      LABELS "all"
      PASS_REGULAR_EXPRESSION "${passRegex}")
  endforeach(testSrc)

  # sanity check short parameter sweeps with checkpoint/restart
  add_test(NAME noodle_sweep_check
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMAND ${CMAKE_SOURCE_DIR}/scripts/sst-sweeper.py 
            ${CMAKE_CURRENT_SOURCE_DIR}/sweep.json
            ${CMAKE_CURRENT_SOURCE_DIR}/noodle-2d.py
            sweep-sanity 
            --tmpdir ${CMAKE_CURRENT_SOURCE_DIR}/run
            --jobname=noodle_sweep_check
	    --clocks=10000
	    --simperiod=2000
            --noprompt)
  set_tests_properties(noodle_sweep_check PROPERTIES
    LABELS "perf"
    TIMEOUT 120)
  add_test(NAME noodle-sweep-check-clean
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_CURRENT_SOURCE_DIR}/run/noodle_sweep_check)
  set_tests_properties(noodle-sweep-check-clean PROPERTIES
    DEPENDS noodle_sweep_check
    LABELS "perf;clean"
    TIMEOUT 10)

endif()

# EOF
