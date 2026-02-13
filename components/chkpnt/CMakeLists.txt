#
# sst-bench/sst-bench/chkpnt CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(ChkpntSrcs
  chkpnt.cc
  chkpnt.h
)

add_library(chkpnt SHARED ${ChkpntSrcs})
target_include_directories(chkpnt PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS chkpnt DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register chkpnt chkpnt_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
