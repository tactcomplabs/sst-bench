//
// _restart_cc_
//
// Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "restart.h"

namespace SST::Restart{

//------------------------------------------
// Restart
//------------------------------------------
Restart::Restart(SST::ComponentId_t id, const SST::Params& params ) :
  SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr),
  numBytes(0), clocks(1000), baseSeed(1223) {

  const uint32_t Verbosity = params.find< uint32_t >( "verbose", 0 );
  output.init(
    "Restart[" + getName() + ":@p:@t]: ",
    Verbosity, 0, SST::Output::STDOUT );
  const std::string cpuClock = params.find< std::string >("clockFreq", "1GHz");
  clockHandler  = new SST::Clock::Handler2<Restart,&Restart::clockTick>(this);
  timeConverter = registerClock(cpuClock, clockHandler);
  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();

  // read the rest of the parameters
  numBytes = (uint64_t)params.find<SST::UnitAlgebra>("numBytes", "64KB").getRoundedValue();
  clocks = params.find<uint64_t>("clocks", 1000);
  baseSeed = params.find<unsigned>("baseSeed", "1223");

  // constructor complete
  output.verbose( CALL_INFO, 5, 0, "Constructor complete\n" );
}

Restart::~Restart(){
}

void Restart::setup(){
}

void Restart::finish(){
}

void Restart::init( unsigned int phase ){
  if( phase == 0 ){
    // setup the internal data
    output.verbose(CALL_INFO, 5, 0,
                   "%s: initializing internal data at init phase=0\n",
                   getName().c_str());
    for( uint64_t i = 0; i < (numBytes/4ull); i++ ){
      data.push_back( (unsigned)(i) + baseSeed );
    }
  }
}

void Restart::printStatus( Output& out ){
}

void Restart::serialize_order(SST::Core::Serialization::serializer& ser){
  SST::Component::serialize_order(ser);
  SST_SER(clockHandler);
  SST_SER(numBytes);
  SST_SER(clocks);
  SST_SER(baseSeed);
  SST_SER(data);
}

bool Restart::clockTick( SST::Cycle_t currentCycle ){

  // sanity check the array
  for( uint64_t i = 0; i < (numBytes/4ull); i++ ){
    if( data[i] != ((unsigned)(i) + baseSeed) ){
      // found a mismatch
      output.fatal( CALL_INFO, -1,
                    "Error : found a mismatch data element: element %" PRIu64 " was %d and should have been %d\n",
                    i, data[i], ((unsigned)(i) + baseSeed));
    }
  }

  // check to see if we've reached the completion state
  if( (uint64_t)(currentCycle) >= clocks ){
    output.verbose(CALL_INFO, 1, 0,
                   "%s ready to end simulation\n",
                   getName().c_str());
    primaryComponentOKToEndSim();
    return true;
  }

  return false;
}

} // namespace SST::Restart

// EOF
