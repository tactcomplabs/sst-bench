#
# sst-bench/components/large-stat CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

if( (${SST_VERSION} STREQUAL "DEV") OR (${SST_VERSION} VERSION_GREATER_EQUAL "15.0") )
  set(LargeStatSrcs
    large-stat.cc
    large-stat.h
  )
else()
  set(LargeStatSrcs
    large-stat-13.1.cc
    large-stat-13.1.h
  )
endif()

add_library(largestat SHARED ${LargeStatSrcs})
target_include_directories(largestat PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS largestat DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register largestat largestat_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
