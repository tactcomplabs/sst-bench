#
# sst-bench/sst-bench CMake
#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

#-- Include Paths
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/include")

message(STATUS "[SST-BENCH] Enabling MSG-PERF micro-benchmark")
add_subdirectory(msg-perf)

message(STATUS "[SST-BENCH] Enabling MICRO-COMP micro-benchmark")
add_subdirectory(micro-comp)

message(STATUS "[SST-BENCH] Enabling MICRO-COMP-LINK micro-benchmark")
add_subdirectory(micro-comp-link)

message(STATUS "[SST-BENCH] Enabling LARGE-STAT micro-benchmark")
add_subdirectory(large-stat)

if( (${SST_VERSION} STREQUAL "DEV") OR (${SST_VERSION} VERSION_GREATER_EQUAL "14.0") )
  message(STATUS "[SST-BENCH] Enabling CHKPNT micro-benchmark")
  add_subdirectory(chkpnt)
  message(STATUS "[SST-BENCH] Enabling RESTORE micro-benchmark")
  add_subdirectory(restore)
  message(STATUS "[SST-BENCH] Enabling RESTART micro-benchmark")
  add_subdirectory(restart)
  message(STATUS "[SST-BENCH] Enabling GRID micro-benchmark")
  add_subdirectory(grid)
endif()

if( (${SST_VERSION} STREQUAL "DEV") OR (${SST_VERSION} VERSION_GREATER_EQUAL "14.1") )
  message(STATUS "[SST-BENCH] Enabling LARGE-STATE-CHKPNT micro-benchmark")
  add_subdirectory(large-stat-chkpnt)
endif()

if( (${SST_VERSION} STREQUAL "DEV") OR (${SST_VERSION} VERSION_GREATER_EQUAL "15.0") )
  message(STATUS "[SST-BENCH] Enabling NOODLE micro-benchmark")
  message(STATUS "[SST-BENCH] Enabling SPAGHETTI micro-benchmark")
  message(STATUS "[SST-BENCH] Enabled PHOLD micro-benchmark")
  add_subdirectory(noodle)
  add_subdirectory(spaghetti)
  add_subdirectory(hpe-phold)
endif()

if(${ENABLE_SSTDBG})
  message(STATUS "[SST-BENCH] Enabling TCL-DBG micro-benchmark")
  add_subdirectory(tcl-dbg)
endif()

# EOF
