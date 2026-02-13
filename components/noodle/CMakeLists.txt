#
# sst-bench/sst-bench/noodle CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(NoodleSrcs
  noodle.cc
  noodle.h
)

add_library(noodle SHARED ${NoodleSrcs})
target_include_directories(noodle PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS noodle DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register noodle noodle_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
