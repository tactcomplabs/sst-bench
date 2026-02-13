#
# sst-bench/sst-bench/spaghetti CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(SpaghettiSrcs
  spaghetti.cc
  spaghetti.h
)

add_library(spaghetti SHARED ${SpaghettiSrcs})
target_include_directories(spaghetti PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS spaghetti DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register spaghetti spaghetti_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
