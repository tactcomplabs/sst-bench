#
# sst-bench/components/restore CMake
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
# See LICENSE in the top level directory for licensing details
#

if( (${SST_VERSION} STREQUAL "DEV") OR (${SST_VERSION} VERSION_GREATER_EQUAL "15.0") )
  set(RestoreSrcs
    restore.cc
    restore.h
  )
else()
  set(RestoreSrcs
    restore-13.1.cc
    restore-13.1.h
  )
endif()

add_library(restore SHARED ${RestoreSrcs})
target_include_directories(restore PUBLIC ${SST_INSTALL_DIR}/include)
install(TARGETS restore DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(CODE "execute_process(COMMAND sst-register restore restore_LIBDIR=${CMAKE_CURRENT_SOURCE_DIR})")

# EOF
