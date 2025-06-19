#
# sst-bench/test/restart CMake
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

file(GLOB RESTART_TEST_SRCS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} *.py)

# Checkpoint numbering version dependent
if(${SST_MAJOR_VERSION} GREATER 14)
  set(CPT_N 1)
else()
  set(CPT_N 0)
endif()

if(SSTBENCH_ENABLE_TESTING)
  set (passRegex "Simulation is complete")

  foreach(testSrc ${RESTART_TEST_SRCS})
    get_filename_component(testName ${testSrc} NAME_WE)
    set(CHKPT_PFX ${testName}_SAVE_)
    add_test(NAME ${testName}_SAVE
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      COMMAND ${SCRIPTS}/sst-chkpt.sh ${CHKPT_PFX} --checkpoint-period=5us --add-lib-path=${CMAKE_BINARY_DIR}/sst-bench/restart ${testSrc})
    set_tests_properties(${testName}_SAVE
      PROPERTIES
      TIMEOUT 60
      LABELS "all"
      PASS_REGULAR_EXPRESSION "${passRegex}")
    add_test(NAME ${testName}_RESTORE
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      COMMAND sst --add-lib-path=${CMAKE_BINARY_DIR}/sst-bench/restore --load-checkpoint ${CHKPT_PFX}/${CHKPT_PFX}_${CPT_N}_5000000/${CHKPT_PFX}_${CPT_N}_5000000.sstcpt)
    set_tests_properties(${testName}_RESTORE
      PROPERTIES
      TIMEOUT 60
      LABELS "all"
      DEPENDS ${testName}_SAVE
      PASS_REGULAR_EXPRESSION "${passRegex}")
  endforeach(testSrc)
endif()

# EOF
