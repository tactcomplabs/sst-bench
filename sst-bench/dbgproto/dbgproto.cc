//
// _dbgproto_cc_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "dbgproto.h"

namespace SST::DbgProto{

//------------------------------------------
// DbgProto
//------------------------------------------
DbgProto::DbgProto(SST::ComponentId_t id, const SST::Params& params ) :
  SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr),
  numPorts(1), minData(1), maxData(2), clockDelay(1), clocks(1000),
  curCycle(0) {

  const int Verbosity = params.find< int >( "verbose", 0 );
  output.init(
    "DbgProto[" + getName() + ":@p:@t]: ",
    Verbosity, 0, SST::Output::STDOUT );
  const std::string cpuClock = params.find< std::string >("clockFreq", "1GHz");
  clockHandler  = new SST::Clock::Handler2<DbgProto,&DbgProto::clockTick>(this);
  timeConverter = registerClock(cpuClock, clockHandler);
  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();

  // read the rest of the parameters
  numPorts = params.find<unsigned>("numPorts", 1);
  minData = params.find<uint64_t>("minData", 1);
  maxData = params.find<uint64_t>("maxData", 2);
  clockDelay = params.find<uint64_t>("clockDelay", 1);
  clocks = params.find<uint64_t>("clocks", 1000);

  // sanity check the params
  if( maxData < minData ){
    output.fatal(CALL_INFO, -1,
                 "%s : maxData < minData\n",
                 getName().c_str());
  }

  // setup the rng
  mersenne = new SST::RNG::MersenneRNG(params.find<unsigned int>("rngSeed", 1223));

  // setup the links
  for( unsigned i=0; i<numPorts; i++ ){
    linkHandlers.push_back(configureLink("port"+std::to_string(i),
                                         new Event::Handler2<DbgProto,
                                         &DbgProto::handleEvent>(this)));
  }

  // debug markers
  markerMsg = "MARKER-" + this->getName();
  // constructor complete
  output.verbose( CALL_INFO, 5, 0, "Constructor complete\n" );
}

DbgProto::~DbgProto(){
}

void DbgProto::setup(){
}

void DbgProto::finish(){
}

void DbgProto::init( unsigned int phase ){
}

void DbgProto::printStatus( Output& out ){
}

#if 1
#define _SER_ SER_INI
#else
#define _SER_ SST_SER
#endif

void DbgProto::serialize_order(SST::Core::Serialization::serializer& ser){
  SST::Component::serialize_order(ser);
  _SER_(clockHandler)
  _SER_(numPorts)
  _SER_(minData)
  _SER_(maxData)
  _SER_(clockDelay)
  _SER_(clocks)
  _SER_(markerMsg)
  _SER_(markerBegin)
  _SER_(curCycle)
  _SER_(markerEnd)
  _SER_(mersenne)
  _SER_(linkHandlers)
}

void DbgProto::handleEvent(SST::Event *ev){
  DbgProtoEvent *cev = static_cast<DbgProtoEvent*>(ev);
  output.verbose(CALL_INFO, 5, 0,
                 "%s: received %zu unsigned values\n",
                 getName().c_str(),
                 cev->getData().size());
  delete ev;
}

void DbgProto::sendData(){
  for( unsigned i=0; i<numPorts; i++ ){
    // generate a new payload
    std::vector<unsigned> data;
    unsigned range = maxData - minData + 1;
    unsigned r = rand() % range + minData;
    for( unsigned i=0; i<r; i++ ){
      data.push_back((unsigned)(mersenne->generateNextUInt32()));
    }
    output.verbose(CALL_INFO, 5, 0,
                   "%s: sending %zu unsigned values on link %d\n",
                   getName().c_str(),
                   data.size(), i);
    DbgProtoEvent *ev = new DbgProtoEvent(data);
    linkHandlers[i]->send(ev);
  }
}

bool DbgProto::clockTick( SST::Cycle_t currentCycle ){

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

} // namespace SST::DbgProto

// EOF
