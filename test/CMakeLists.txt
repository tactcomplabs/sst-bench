#
# sst-bench/test CMake
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
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
  message(STATUS "[SST-BENCH] Enabling RESTORE testing")
  add_subdirectory(restore)
  message(STATUS "[SST-BENCH] Enabling RESTART testing")
  add_subdirectory(restart)
endif()

if(${SST_MAJOR_VERSION} EQUAL 14)
  if(${SST_MINOR_VERSION} EQUAL 1)
    message(STATUS "[SST-BENCH] Enabling LARGE-STATE-CHKPNT testing")
    add_subdirectory(large-stat-chkpnt)
  endif()
elseif(${SST_MAJOR_VERSION} GREATER 14)
  message(STATUS "[SST-BENCH] Enabling LARGE-STATE-CHKPNT testing")
  add_subdirectory(large-stat-chkpnt)
endif()

if(${ENABLE_SSTDBG})
  message(STATUS "[SST-BENCH] Enabling TCL-DBG testing")
  add_subdirectory(tcl-dbg)
endif()

# EOF
