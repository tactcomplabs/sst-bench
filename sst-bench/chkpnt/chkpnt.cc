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
  SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr),
  numPorts(1), minData(1), maxData(2), clockDelay(1), clocks(1000),
  curCycle(0) {

  const int Verbosity = params.find< int >( "verbose", 0 );
  output.init(
    "Chkpnt[" + getName() + ":@p:@t]: ",
    Verbosity, 0, SST::Output::STDOUT );
  const std::string cpuClock = params.find< std::string >("clockFreq", "1GHz");
  clockHandler  = new SST::Clock::Handler2<Chkpnt,&Chkpnt::clockTick>(this);
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
                                         new Event::Handler2<Chkpnt,
                                         &Chkpnt::handleEvent>(this)));
  }

  // debug marker
  markerMsg = "MARKER-" + this->getName();
  // constructor complete
  output.verbose( CALL_INFO, 5, 0, "Constructor complete\n" );
}

Chkpnt::~Chkpnt(){
}

void Chkpnt::setup(){
}

void Chkpnt::finish(){
}

void Chkpnt::init( unsigned int phase ){
}

void Chkpnt::printStatus( Output& out ){
}

#if 1
#define _SER_ SER_INI
#else
#define _SER_ SST_SER
#endif

void Chkpnt::serialize_order(SST::Core::Serialization::serializer& ser){
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

void Chkpnt::handleEvent(SST::Event *ev){
  ChkpntEvent *cev = static_cast<ChkpntEvent*>(ev);
  output.verbose(CALL_INFO, 5, 0,
                 "%s: received %zu unsigned values\n",
                 getName().c_str(),
                 cev->getData().size());
  delete ev;
}

void Chkpnt::sendData(){
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
    ChkpntEvent *ev = new ChkpntEvent(data);
    linkHandlers[i]->send(ev);
  }
}

bool Chkpnt::clockTick( SST::Cycle_t currentCycle ){

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

} // namespace SST::Chkpnt

// EOF
