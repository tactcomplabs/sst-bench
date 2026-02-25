//
// _flood_cc_
//
// Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "flood.h"

namespace SST::Flood{

//------------------------------------------
// Flood
//------------------------------------------
Flood::Flood( SST::ComponentId_t id, const SST::Params& params ) :
  SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr),
  numPorts(2), msgsPerClock(8), gbPerMsg(1), portsPerClock(1),
  clocks(10000), rngSeed(31337), hubComp(false) {

  uint32_t Verbosity = params.find< uint32_t >( "verbose", 0 );
  output.init(
    "Flood[" + getName() + ":@p:@t]: ",
    Verbosity, 0, SST::Output::STDOUT );

  // setup the clock handler
  clockHandler  = new SST::Clock::Handler2<Flood,&Flood::clockTick>(this);
  const std::string cpuClock = params.find<std::string>("clockFreq", "1GHz");
  timeConverter = registerClock(cpuClock, clockHandler);

  // register our component
  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();

  // gather all the parameters
  numPorts = params.find<uint64_t>("numPorts", 2);
  msgsPerClock = params.find<uint64_t>("msgsPerClock", 8);
  gbPerMsg = params.find<uint64_t>("gigabytePerMsg", 1);
  portsPerClock = params.find<uint64_t>("portsPerClock", 1);
  clocks = params.find<uint64_t>("clocks", 10000);
  rngSeed = params.find<uint32_t>("rngSeed", 31337);
  hubComp = params.find<bool>("hubComp", false);

  // sanity check the port configs
  if( portsPerClock > numPorts ){
    output.fatal( CALL_INFO, -1, "%s : numPorts < portsPerClock\n",
                 getName().c_str());
  }

  // setup the port handlers
  portname.resize(numPorts);
  linkHandlers.resize(numPorts);
  for( uint64_t i=0; i<numPorts; i++ ){
    portname[i] = "port" + std::to_string(i);
    linkHandlers[i] = configureLink("port"+std::to_string(i),
                                    new Event::Handler2<Flood,
                                    &Flood::handleEvent>(this));
  }

  // setup the local random number generator
  localRNG = new SST::RNG::MersenneRNG(uint32_t(id) + rngSeed);

  // constructor complete
  output.verbose( CALL_INFO, 5, 0, "Constructor complete\n" );
}

Flood::~Flood(){
  if (localRNG) delete localRNG;
}

void Flood::setup(){
}

void Flood::finish(){
}

void Flood::init( unsigned int phase ){
}

void Flood::handleEvent(SST::Event *ev){
  FloodEvent *ne = static_cast<FloodEvent*>(ev);
  if( ne == nullptr ){
    output.fatal( CALL_INFO, -1, "%s : null message arrived\n",
                 getName().c_str());
  }
  packet = ne->getData();
  output.verbose(CALL_INFO, 5, 0,
                 "%s: received %zu bytes\n",
                 getName().c_str(),
                 packet.size()*8);
  packet.clear();
  delete ev;
}

void Flood::sendData(){
  std::vector<uint64_t> sendPorts;

  // build a list of ports to send data over, note that there can be duplicates
  if( numPorts > 1 ){
    for( uint64_t i=0; i<portsPerClock; i++ ){
      sendPorts.push_back(localRNG->generateNextUInt64() % (numPorts-1));
    }
  }else{
    // single port configured
    sendPorts.push_back(0);
  }

  // build a sample packet
  packet.clear();
  packet.resize(gbPerMsg*_U641GB_);
  for( uint64_t s = 0x00ull; s < (gbPerMsg*_U641GB_); s++ ){
    packet.push_back( (uint64_t)(localRNG->generateNextUInt64()) );
  }

  // build packets for each port
  for( const auto &p : sendPorts ){
    // build some number of packets for port `p`
    output.verbose( CALL_INFO, 9, 0, "sendData for port = %s\n",
                    portname[p].c_str() );
    for( uint64_t m = 0x00ull; m < msgsPerClock; m++ ){
      // send message 'm' through port 'p'
      FloodEvent *ne = new FloodEvent(packet);
      linkHandlers[p]->send(ne);
    }
  }
}

bool Flood::clockTick(SST::Cycle_t currentCycle){
  if( (uint64_t)(currentCycle) >= clocks ){
    output.verbose(CALL_INFO, 1, 0,
                   "%s is ready to end simulation\n",
                   getName().c_str());
    primaryComponentOKToEndSim();
    return true;
  }

  // only send events if we're the hub component
  if( hubComp ){
    sendData();
  }

  return false;
}

} // namespace SST::Flood

// EOF
