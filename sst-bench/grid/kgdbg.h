//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
// See LICENSE in the top level directory for licensing details
//

#ifndef _KGDBG_H
#define _KGDBG_H

#include <iostream>
#include <unistd.h>

namespace kgdbg {

static inline void spinner( const char* id, bool cond = true ) {
  if( !std::getenv( id ) )
    return;
  if( !cond )
    return;
  unsigned long spinner = 1;
  while( spinner > 0 ) {
    std::cout << id << " spinning PID " << getpid() << std::endl;
    spinner++;
    sleep( 5 );
  }
  std::cout << std::endl;
}
}  //namespace kgdbg

#endif  //_KGDBG_H
