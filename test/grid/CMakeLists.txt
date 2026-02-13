#
# sst-bench/test/grid CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

file(GLOB GRID_TEST_SRCS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} 2d.py)

# Checkpoint numbering version dependent
if(${SST_MAJOR_VERSION} GREATER 14)
  set(CPT_N 101)
else()
  set(CPT_N 100)
endif()

if(SSTBENCH_ENABLE_TESTING)
  set (passRegex "Simulation is complete")

  foreach(testSrc ${GRID_TEST_SRCS})
    get_filename_component(testName ${testSrc} NAME_WE)
    set(CHKPT_PFX ${testName}_SAVE_)
    add_test(NAME ${testName}_SAVE
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      COMMAND ${SCRIPTS}/sst-chkpt.sh ${CHKPT_PFX} --checkpoint-period=10ns --add-lib-path=${CMAKE_BINARY_DIR}/sst-bench/grid ${testSrc})
    set_tests_properties(${testName}_SAVE PROPERTIES
      TIMEOUT 120
      LABELS "all"
      PASS_REGULAR_EXPRESSION "${passRegex}")
    add_test(NAME ${testName}_RESTORE
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      COMMAND sst --add-lib-path=${CMAKE_BINARY_DIR}/sst-bench/grid --load-checkpoint ${CHKPT_PFX}/${CHKPT_PFX}_${CPT_N}_1010000/${CHKPT_PFX}_${CPT_N}_1010000.sstcpt)
    set_tests_properties(${testName}_RESTORE PROPERTIES
      TIMEOUT 120
      LABELS "all"
      DEPENDS ${testName}_SAVE
      PASS_REGULAR_EXPRESSION "${passRegex}")
  endforeach(testSrc)

  # if (MPIEXEC_EXECUTABLE)
  #   # TODO qualify with version
  #   # Also make sure ./run is clean
  #   # Need to be able to pass sst options: --add-lib-path=${CMAKE_BINARY_DIR}/sst-bench/grid
  #   # sanity check short parameter sweeps with checkpoint/restart
  #   add_test(NAME grid_sweep_check
  #     WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  #     COMMAND ${CMAKE_SOURCE_DIR}/scripts/sst-sweeper.py 
  #             ${CMAKE_CURRENT_SOURCE_DIR}/sweep.json
  #             ${CMAKE_CURRENT_SOURCE_DIR}/2d.py
  #             sweep-sanity 
  #             --tmpdir ${CMAKE_CURRENT_SOURCE_DIR}/run
  #             --jobname=grid_sweep_check
  #       --clocks=10000
  #       --simperiod=2000
  #             --noprompt)
  #   set_tests_properties(grid_sweep_check PROPERTIES
  #     LABELS "perf"
  #     TIMEOUT 120)
  #   add_test(NAME grid-sweep-check-clean
  #     WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  #     COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_CURRENT_SOURCE_DIR}/run/grid_sweep_check)
  #   set_tests_properties(grid-sweep-check-clean PROPERTIES
  #     DEPENDS grid_sweep_check
  #     LABELS "perf;clean"
  #     TIMEOUT 10)
  # endif()

endif()

# EOF
