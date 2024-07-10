//
// _large-stat_cc_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "large-stat.h"

namespace SST::LargeStat{

  //------------------------------------------
  // LargeStat
  //------------------------------------------
  LargeStat::LargeStat(SST::ComponentId_t id, const SST::Params& params ) :
    SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr),
    numStats(1) {
    const int Verbosity = params.find< int >( "verbose", 0 );
    output.init(
      "LargeStat[" + getName() + ":@p:@t]: ",
      Verbosity, 0, SST::Output::STDOUT );
    output.verbose( CALL_INFO, 5, 0, "Init is complete\n" );
    clockHandler  = new SST::Clock::Handler<LargeStat>(this,
                                                       &LargeStat::clockTick);
    timeConverter = registerClock("1GHz", clockHandler);
    registerAsPrimaryComponent();
    primaryComponentDoNotEndSim();

    // read the remainder of the parameters
    numStats = params.find<uint64_t>( "numStats", 1 );

    // initialize the statistics
    for( auto i = 0x00ull; i<numStats; i++ ){
      std::string sName = std::to_string(i);
      VStat.push_back(registerStatistic<uint64_t>("STAT_", sName));
    }
  }

  LargeStat::~LargeStat(){
  }

  void LargeStat::setup(){
  }

  void LargeStat::finish(){
  }

  void LargeStat::init( unsigned int phase ){
  }

  bool LargeStat::clockTick( SST::Cycle_t currentCycle ){
    primaryComponentOKToEndSim();
    return true;
  }
}

// EOF
