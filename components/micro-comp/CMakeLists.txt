#
# sst-bench/sst-bench/micro-comp CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(MicroCompSrcs
  micro-comp.cc
  micro-comp.h
)

add_library(microcomp SHARED ${MicroCompSrcs})
target_include_directories(microcomp PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS microcomp DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register microcomp microcomp_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
