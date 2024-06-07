#
# sst-bench/sst-bench/restore CMake
#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(RestoreSrcs
  restore.cc
  restore.h
)

add_library(restore SHARED ${RestoreSrcs})
target_include_directories(restore PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS restore DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register restore restore_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
