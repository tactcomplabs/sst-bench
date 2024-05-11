//
// _micro-comp_cc_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "micro-comp.h"

namespace SST::MicroComp{

  //------------------------------------------
  // MicroComp
  //------------------------------------------
  MicroComp::MicroComp(SST::ComponentId_t id, const SST::Params& params ) :
    SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr) {
    const int Verbosity = params.find< int >( "verbose", 0 );
    output.init(
      "MicroComp[" + getName() + ":@p:@t]: ",
      Verbosity, 0, SST::Output::STDOUT );
    output.verbose( CALL_INFO, 5, 0, "Init is complete\n" );
    clockHandler  = new SST::Clock::Handler<MicroComp>(this,
                                                       &MicroComp::clockTick);
    timeConverter = registerClock("1GHz", clockHandler);
    registerAsPrimaryComponent();
    primaryComponentDoNotEndSim();
  }

  MicroComp::~MicroComp(){
  }

  void MicroComp::setup(){
  }

  void MicroComp::finish(){
  }

  void MicroComp::init( unsigned int phase ){
  }

  bool MicroComp::clockTick( SST::Cycle_t currentCycle ){
    primaryComponentOKToEndSim();
    return true;
  }

}

// EOF
