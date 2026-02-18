#
# sst-bench/components/hpe-phold CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(PholdSrcs
  Node.cc
  Node.h
)

add_library(phold SHARED ${PholdSrcs})
target_include_directories(phold PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS phold DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register phold phold_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
