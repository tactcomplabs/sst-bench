#
# sst-bench/components/large-stat-chkpnt CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

if( (${SST_VERSION} STREQUAL "DEV") OR (${SST_VERSION} VERSION_GREATER_EQUAL "15.0") )
  set(LargeStatChkpntSrcs
    large-stat-chkpnt.cc
    large-stat-chkpnt.h
  )
else()
  set(LargeStatChkpntSrcs
    large-stat-chkpnt-13.1.cc
    large-stat-chkpnt-13.1.h
  )
endif()

add_library(largestatchkpnt SHARED ${LargeStatChkpntSrcs})
target_include_directories(largestatchkpnt PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS largestatchkpnt DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register largestatchkpnt largestatchkpnt_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
