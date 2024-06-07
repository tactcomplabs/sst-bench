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
endif()

# EOF
