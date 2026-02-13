#
# sst-bench/sst-bench/micro-comp-link CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(MicroCompLinkSrcs
  micro-comp-link.cc
  micro-comp-link.h
)

add_library(microcomplink SHARED ${MicroCompLinkSrcs})
target_include_directories(microcomplink  PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS microcomplink DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register microcomplink microcomplink_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
