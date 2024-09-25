//
// _large-stat-chkpnt_cc_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "large-stat-chkpnt.h"

namespace SST::LargeStatChkpnt{

  //------------------------------------------
  // LargeStatChkpnt
  //------------------------------------------
  LargeStatChkpnt::LargeStatChkpnt(SST::ComponentId_t id, const SST::Params& params ) :
    SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr),
    numStats(1), numClocks(1) {
    const int Verbosity = params.find< int >( "verbose", 0 );
    output.init(
      "LargeStatChkpnt[" + getName() + ":@p:@t]: ",
      Verbosity, 0, SST::Output::STDOUT );
    output.verbose( CALL_INFO, 5, 0, "Init is complete\n" );
    clockHandler  = new SST::Clock::Handler2<LargeStatChkpnt,
                  &LargeStatCkpnt::clockTick>(this);
    timeConverter = registerClock("1GHz", clockHandler);
    registerAsPrimaryComponent();
    primaryComponentDoNotEndSim();

    // read the remainder of the parameters
    numStats = params.find<uint64_t>( "numStats", 1 );
    numClocks = params.find<uint64_t>( "numClocks", 1);

    // initialize the statistics
    for( auto i = 0x00ull; i<numStats; i++ ){
      std::string sName = std::to_string(i);
      VStat.push_back(registerStatistic<uint64_t>("STAT_", sName));
    }
  }

  LargeStatChkpnt::~LargeStatChkpnt(){
  }

  void LargeStatChkpnt::setup(){
  }

  void LargeStatChkpnt::finish(){
  }

  void LargeStatChkpnt::init( unsigned int phase ){
  }

  void LargeStatChkpnt::serialize_order(SST::Core::Serialization::serializer& ser){
    SST::Component::serialize_order(ser);
    SST_SER(clockHandler)
    SST_SER(numStats)
    SST_SER(numClocks)
    SST_SER(VStat)
  }

  bool LargeStatChkpnt::clockTick( SST::Cycle_t currentCycle ){
    if( (uint64_t)(currentCycle) >= numClocks ){
      primaryComponentOKToEndSim();
      return true;
    }
    return false;
  }
}

// EOF
