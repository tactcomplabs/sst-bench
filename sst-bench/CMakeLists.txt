#
# sst-bench/sst-bench CMake
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

message(STATUS "[SST-BENCH] Enabling MSG-PERF micro-benchmark")
add_subdirectory(msg-perf)

message(STATUS "[SST-BENCH] Enabling MICRO-COMP micro-benchmark")
add_subdirectory(micro-comp)

if(${SST_MAJOR_VERSION} GREATER_EQUAL 14)
  message(STATUS "[SST-BENCH] Enabling CHKPNT micro-benchmark")
  add_subdirectory(chkpnt)
  message(STATUS "[SST-BENCH] Enabling RESTORE micro-benchmark")
  add_subdirectory(restore)
  message(STATUS "[SST-BENCH] Enabling RESTART micro-benchmark")
  add_subdirectory(restart)
endif()

if (${SST_VERSION} STREQUAL "14.0.0.kg")
  message(STATUS "[SST-BENCH] Enabling DBGPROTO micro-benchmark")
  add_subdirectory(dbgproto)
else()
  message(WARNING "[SST-BENCH] DBGPROTO requires sst version 14.0.0.kg")
endif()

# EOF
