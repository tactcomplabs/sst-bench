#
# sst-bench/components/micro-comp-link CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

if( (${SST_VERSION} STREQUAL "DEV") OR (${SST_VERSION} VERSION_GREATER_EQUAL "15.0") )
  set(MicroCompLinkSrcs
    micro-comp-link.cc
    micro-comp-link.h
  )
else()
  set(MicroCompLinkSrcs
    micro-comp-link-13.1.cc
    micro-comp-link-13.1.h
  )
endif()


add_library(microcomplink SHARED ${MicroCompLinkSrcs})
target_include_directories(microcomplink  PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS microcomplink DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register microcomplink microcomplink_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
