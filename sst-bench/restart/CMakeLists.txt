#
# sst-bench/sst-bench/restart CMake
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(RestartSrcs
  restart.cc
  restart.h
)

add_library(restart SHARED ${RestartSrcs})
target_include_directories(restart PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS restart DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register restart restart_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
