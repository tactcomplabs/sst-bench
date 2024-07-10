#
# sst-bench/sst-bench/large-stat CMake
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(LargeStatSrcs
  large-stat.cc
  large-stat.h
)

add_library(largestat SHARED ${LargeStatSrcs})
target_include_directories(largestat PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS largestat DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register largestat largestat_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
