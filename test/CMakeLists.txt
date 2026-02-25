#
# sst-bench/test CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

message(STATUS "[SST-BENCH] Enabling MSG-PERF testing")
add_subdirectory(msg-perf)
message(STATUS "[SST-BENCH] Enabling MICRO-COMP testing")
add_subdirectory(micro-comp)
message(STATUS "[SST-BENCH] Enabling MICRO-COMP-LINK testing")
add_subdirectory(micro-comp-link)
message(STATUS "[SST-BENCH] Enabling LARGE-STAT testing")
add_subdirectory(large-stat)

if( (${SST_VERSION} STREQUAL "DEV") OR (${SST_VERSION} VERSION_GREATER_EQUAL "14.0") )
  message(STATUS "[SST-BENCH] Enabling CHKPNT testing")
  add_subdirectory(chkpnt)
endif()

if( (${SST_VERSION} STREQUAL "DEV") OR (${SST_VERSION} VERSION_GREATER_EQUAL "14.1") )
  message(STATUS "[SST-BENCH] Enabling LARGE-STATE-CHKPNT testing")
  add_subdirectory(large-stat-chkpnt)
  message(STATUS "[SST-BENCH] Enabling RESTORE testing")
  add_subdirectory(restore)
  message(STATUS "[SST-BENCH] Enabling RESTART testing")
  add_subdirectory(restart)
  message(STATUS "[SST-BENCH] Enabling GRID testing")
  add_subdirectory(grid)
  message(STATUS "[SST-BENCH] Enabling FLOOD testing")
  add_subdirectory(flood)
endif()

if( (${SST_VERSION} STREQUAL "DEV") OR (${SST_VERSION} VERSION_GREATER_EQUAL "15.0") )
  message(STATUS "[SST-BENCH] Enabling NOODLE testing")
  message(STATUS "[SST-BENCH] Enabling SPAGHETTI testing")
  add_subdirectory(noodle)
  add_subdirectory(spaghetti)
  message(STATUS "[SST-BENCH] Enabling HPE-PHOLD testing")
  add_subdirectory(hpe-phold)
endif()

# TODO replace with interactive console micro-benchmarks
# if(${ENABLE_SSTDBG})
#   message(STATUS "[SST-BENCH] Enabling TCL-DBG testing")
#   add_subdirectory(tcl-dbg)
# endif()

# EOF
