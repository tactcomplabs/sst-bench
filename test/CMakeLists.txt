#
# sst-bench/test CMake
#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
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

if(${SST_MAJOR_VERSION} GREATER_EQUAL 14)
  message(STATUS "[SST-BENCH] Enabling CHKPNT testing")
  add_subdirectory(chkpnt)
endif()

set(SST_14_1_MIN 0)
if(${SST_MAJOR_VERSION} EQUAL 14)
  if(${SST_MINOR_VERSION} GREATER_EQUAL 1)
    set(SST_14_1_MIN 1)
  endif()
elseif(${SST_MAJOR_VERSION} GREATER 14)
  set(SST_14_1_MIN 1)
endif()

if(${SST_14_1_MIN})
  message(STATUS "[SST-BENCH] Enabling LARGE-STATE-CHKPNT testing")
  add_subdirectory(large-stat-chkpnt)
  message(STATUS "[SST-BENCH] Enabling RESTORE testing")
  add_subdirectory(restore)
  message(STATUS "[SST-BENCH] Enabling RESTART testing")
  add_subdirectory(restart)
  message(STATUS "[SST-BENCH] Enabling GRID testing")
  add_subdirectory(grid)
endif()

if(${ENABLE_SSTDBG})
  message(STATUS "[SST-BENCH] Enabling TCL-DBG testing")
  add_subdirectory(tcl-dbg)
endif()

# EOF
