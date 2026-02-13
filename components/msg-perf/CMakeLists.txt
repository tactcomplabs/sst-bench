#
# sst-bench/components/msg-perf CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(MsgPerfSrcs
  msg-perf.cc
  msg-perf.h
)

add_library(msgperf SHARED ${MsgPerfSrcs})
target_include_directories(msgperf  PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS msgperf DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register msgperf msgperf_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
