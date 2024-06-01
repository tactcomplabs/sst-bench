//
// _chkpnt_cc_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "chkpnt.h"

namespace SST::Chkpnt{

  //------------------------------------------
  // Chkpnt
  //------------------------------------------
  Chkpnt::Chkpnt(SST::ComponentId_t id, const SST::Params& params ) :
    SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr) {
    const int Verbosity = params.find< int >( "verbose", 0 );
    output.init(
      "Chkpnt[" + getName() + ":@p:@t]: ",
      Verbosity, 0, SST::Output::STDOUT );
    output.verbose( CALL_INFO, 5, 0, "Init is complete\n" );
    clockHandler  = new SST::Clock::Handler<Chkpnt>(this,
                                                       &Chkpnt::clockTick);
    timeConverter = registerClock("1GHz", clockHandler);
    registerAsPrimaryComponent();
    primaryComponentDoNotEndSim();
  }

  Chkpnt::~Chkpnt(){
  }

  void Chkpnt::setup(){
  }

  void Chkpnt::finish(){
  }

  void Chkpnt::init( unsigned int phase ){
  }

  bool Chkpnt::clockTick( SST::Cycle_t currentCycle ){
    primaryComponentOKToEndSim();
    return true;
  }

}

// EOF
