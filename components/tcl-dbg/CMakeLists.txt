#
# sst-bench/components/tcl-dbg CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

set(TclDbgSrcs
  tcl-dbg.cc
  tcl-dbg.h
)

add_library(tcldbg SHARED ${TclDbgSrcs})
target_include_directories(tcldbg PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS tcldbg DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register tcldbg tcldbg_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
