//
// _gridcomp_cc_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "gridcomp.h"

namespace SST::GridComp{

//------------------------------------------
// GridComp
//------------------------------------------
GridComp::GridComp(SST::ComponentId_t id, const SST::Params& params ) :
  SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr),
  numPorts(1), minData(1), maxData(2), clockDelay(1), clocks(1000),
  curCycle(0) {

  const int Verbosity = params.find< int >( "verbose", 0 );
  output.init(
    "GridComp[" + getName() + ":@p:@t]: ",
    Verbosity, 0, SST::Output::STDOUT );
  const std::string cpuClock = params.find< std::string >("clockFreq", "1GHz");
  clockHandler  = new SST::Clock::Handler2<GridComp,&GridComp::clockTick>(this);
  timeConverter = registerClock(cpuClock, clockHandler);
  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();

  // read the rest of the parameters
  numBytes = params.find<SST::UnitAlgebra>("numBytes", "64KB").getRoundedValue();
  numPorts = params.find<unsigned>("numPorts", 1);
  minData = params.find<uint64_t>("minData", 1);
  maxData = params.find<uint64_t>("maxData", 2);
  clockDelay = params.find<uint64_t>("clockDelay", 1);
  clocks = params.find<uint64_t>("clocks", 1000);
  baseSeed = params.find<unsigned>("baseSeed", "1223");

  // sanity check the params
  if( maxData < minData ){
    output.fatal(CALL_INFO, -1,
                 "%s : maxData < minData\n",
                 getName().c_str());
  }

  // setup the rng
  rngSend = new SST::RNG::MersenneRNG(params.find<unsigned int>("rngSeed", 1223));
  rngRcv  = new SST::RNG::MersenneRNG(params.find<unsigned int>("rngSeed", 1223));

  // setup the links
  for( unsigned i=0; i<numPorts; i++ ){
    linkHandlers.push_back(configureLink("port"+std::to_string(i),
                                         new Event::Handler2<GridComp,
                                         &GridComp::handleEvent>(this)));
  }

  // constructor complete
  output.verbose( CALL_INFO, 5, 0, "Constructor complete\n" );
}

GridComp::~GridComp(){
}

void GridComp::setup(){
}

void GridComp::finish(){
}

void GridComp::init( unsigned int phase ){
  if( phase == 0 ){
    // setup the initial data
    output.verbose(CALL_INFO, 5, 0,
                   "%s: initializing internal data at init phase=0\n",
                   getName().c_str());
    for( uint64_t i = 0; i < (numBytes/4ull); i++ ){
      data.push_back( (unsigned)(i) + baseSeed );
    }
  }
}

void GridComp::printStatus( Output& out ){
}

void GridComp::serialize_order(SST::Core::Serialization::serializer& ser){
  SST::Component::serialize_order(ser);
  SST_SER(clockHandler)
  SST_SER(numBytes)
  SST_SER(numPorts)
  SST_SER(minData)
  SST_SER(maxData)
  SST_SER(clockDelay)
  SST_SER(clocks)
  SST_SER(baseSeed)
  SST_SER(data)
  SST_SER(curCycle)
  SST_SER(rngSend)
  SST_SER(rngRcv)
  SST_SER(linkHandlers)
}

void GridComp::handleEvent(SST::Event *ev){
  GridCompEvent *cev = static_cast<GridCompEvent*>(ev);
  auto data = cev->getData();
  output.verbose(CALL_INFO, 5, 0,
                 "%s: received %zu unsigned values\n",
                 getName().c_str(),
                 data.size());
  // Check the incoming data
  unsigned range = maxData - minData + 1;
  unsigned r = rngRcv->generateNextUInt32() % range + minData;
  if (r != data.size()) {
    output.fatal(CALL_INFO, -1,
                  "Expected data size %" PRIu32 " does not match actual size %" PRIu64 "\n",
                  r, data.size());
  }
  if (r != data[0]) {
    output.fatal(CALL_INFO, -1,
              "Expected data[0] %" PRIu32 " does not match actual %" PRIu32 "\n",
              r, data[0]);
  }
  for (unsigned i=1; i<r; i++){
    unsigned d = (unsigned)rngRcv->generateNextUInt32();
    if ( d != data[i] ) {
      output.fatal(CALL_INFO, -1,
          "Expected data[%" PRIu32 "] %" PRIu32 " does not match actual %" PRIu32 "\n",
          i, d, data[i]);
    }
  }
  
  delete ev;
}

void GridComp::sendData(){
  for( unsigned i=0; i<numPorts; i++ ){
    // generate a new payload
    std::vector<unsigned> data;
    unsigned range = maxData - minData + 1;
    unsigned r = rngSend->generateNextUInt32() % range + minData;
    // First data is the number of ints
    data.push_back(r);
    for( unsigned i=1; i<r; i++ ){
      data.push_back((unsigned)(rngSend->generateNextUInt32()));
    }
    output.verbose(CALL_INFO, 5, 0,
                   "%s: sending %zu unsigned values on link %d\n",
                   getName().c_str(),
                   data.size(), i);
    GridCompEvent *ev = new GridCompEvent(data);
    linkHandlers[i]->send(ev);
  }
}

bool GridComp::clockTick( SST::Cycle_t currentCycle ){

  // sanity check the array
  for( uint64_t i = 0; i < (numBytes/4ull); i++ ){
    if( data[i] != ((unsigned)(i) + baseSeed) ){
      // found a mismatch
      output.fatal( CALL_INFO, -1,
                    "Error : found a mismatch data element: element %" PRIu64 " was %d and should have been %d\n",
                    i, data[i], ((unsigned)(i) + baseSeed));
    }
  }

  // check to see whether we need to send data over the links
  curCycle++;
  if( curCycle >= clockDelay ){
    sendData();
    curCycle = 0;
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

} // namespace SST::GridComp

// EOF
