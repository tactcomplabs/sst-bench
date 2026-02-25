#
# sst-bench/components/flood CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(FloodSrcs
  flood.cc
  flood.h
)

add_library(flood SHARED ${FloodSrcs})
target_include_directories(flood PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS flood DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register flood flood_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
