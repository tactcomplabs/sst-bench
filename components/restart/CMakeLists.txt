#
# sst-bench/components/restart CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

if( (${SST_VERSION} STREQUAL "DEV") OR (${SST_VERSION} VERSION_GREATER_EQUAL "15.0") )
  set(RestartSrcs
    restart.cc
    restart.h
  )
else()
  set(RestartSrcs
    restart-13.1.cc
    restart-13.1.h
  )
endif()

add_library(restart SHARED ${RestartSrcs})
target_include_directories(restart PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS restart DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register restart restart_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
