#
# sst-bench/components/grid CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

if( (${SST_VERSION} STREQUAL "DEV") OR (${SST_VERSION} VERSION_GREATER_EQUAL "15.0") )
  set(GridSrcs
    gridnode.cc
    gridnode.h
  )
else()
  set(GridSrcs
    gridnode-13.1.cc
    gridnode-13.1.h
  )
endif()

add_library(grid SHARED ${GridSrcs})
target_include_directories(grid PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS grid DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register grid grid_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
