#
# sst-bench/sst-bench/dbgsock CMake
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(DbgSockSrcs
  dbgsock.cc
  dbgsock.h
)

add_library(dbgsock SHARED ${DbgSockSrcs})
target_include_directories(dbgsock PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS dbgsock DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register dbgsock dbgsock_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
