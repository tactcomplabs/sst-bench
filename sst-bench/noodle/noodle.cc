//
// _noodle_cc_
//
// Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "noodle.h"

namespace SST::Noodle{

//------------------------------------------
// Noodle
//------------------------------------------
Noodle::Noodle(SST::ComponentId_t id, const SST::Params& params ) :
  SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr),
  numPorts(2), msgsPerClock(8), bytesPerClock(8), portsPerClock(1),
  clocks(10000), rngSeed(31337) {

  uint32_t Verbosity = params.find< uint32_t >( "verbose", 0 );
  output.init(
    "Noodle[" + getName() + ":@p:@t]: ",
    Verbosity, 0, SST::Output::STDOUT );

  // determine our target clock frequency
  clockHandler  = new SST::Clock::Handler2<Noodle,&Noodle::clockTick>(this);
  if( params.contains("randClockRange") ){
    // derive the target clock frequency range and randomly select a new clock frequency
    const std::string clockRange = params.find<std::string>("randClockRange", "1-2");
    size_t dashPos = clockRange.find('-');
    float minValue = std::stof(clockRange.substr(0, dashPos));
    float maxValue = std::stof(clockRange.substr(dashPos + 1));
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> dist(minValue, maxValue);
    float randomValue = dist(gen);
    std::string randomValueString = std::to_string(randomValue) + "GHz";
    timeConverter = registerClock(randomValueString, clockHandler);
    output.verbose( CALL_INFO, 5, 0, "Clock frequency set to: %s\n",
                    randomValueString.c_str() );
  }else{
    // use the standard clockFreq parameter or the default value of 1GHz
    const std::string cpuClock = params.find<std::string>("clockFreq", "1GHz");
    timeConverter = registerClock(cpuClock, clockHandler);
  }

  // register our component
  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();

  // read the rest of the parameters
  numPorts = params.find<uint64_t>("numPorts", 2);
  msgsPerClock = params.find<uint64_t>("msgsPerClock", 8);
  bytesPerClock = params.find<uint64_t>("bytesPerClock", 8);
  portsPerClock = params.find<uint64_t>("portsPerClock", 1);
  clocks = params.find<uint64_t>("clocks", 10000);
  rngSeed = params.find<uint32_t>("rngSeed", 31337);

  // sanity check the port configs
  if( portsPerClock > numPorts ){
    output.fatal( CALL_INFO, -1, "%s : numPorts < portsPerClock\n",
                 getName().c_str());
  }

  // setup the port handlers
  portname.resize(numPorts);
  for( uint64_t i=0; i<numPorts; i++ ){
    portname[i] = "port" + std::to_string(i);
    linkHandlers.push_back(configureLink("port"+std::to_string(i),
                                         new Event::Handler2<Noodle,
                                         &Noodle::handleEvent>(this)));
  }

  // setup the local random number generator
  localRNG = new SST::RNG::MersenneRNG(uint32_t(id) + rngSeed);

  // constructor complete
  output.verbose( CALL_INFO, 5, 0, "Constructor complete\n" );
}

Noodle::~Noodle(){
  if (localRNG) delete localRNG;
}

void Noodle::setup(){
}

void Noodle::finish(){
}

void Noodle::init( unsigned int phase ){
}

void Noodle::handleEvent(SST::Event *ev){
  NoodleEvent *ne = static_cast<NoodleEvent*>(ev);
  auto data = ne->getData();
  output.verbose(CALL_INFO, 5, 0,
                 "%s: received %zu bytes\n",
                 getName().c_str(),
                 data.size());
  delete ev;
}

void Noodle::sendData(){
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
  std::vector<uint8_t> packet;
  for( uint64_t s = 0x00ull; s < bytesPerClock; s++ ){
    packet.push_back( (uint8_t)(localRNG->generateNextUInt32() & 0b11111111) );
  }

  // build packets for each port
  for( const auto &p : sendPorts ){
    // build some number of packets for port `p`
    output.verbose( CALL_INFO, 9, 0, "sendData for port = %s\n",
                    portname[p].c_str() );
    for( uint64_t m = 0x00ull; m < msgsPerClock; m++ ){
      // send message 'm' through port 'p'
      NoodleEvent *ne = new NoodleEvent(packet);
      linkHandlers[p]->send(ne);
    }
  }
}

bool Noodle::clockTick(SST::Cycle_t currentCycle){
  if( (uint64_t)(currentCycle) >= clocks ){
    output.verbose(CALL_INFO, 1, 0,
                   "%s is ready to end simulation\n",
                   getName().c_str());
    primaryComponentOKToEndSim();
    return true;
  }

  sendData();

  return false;
}

} // namespace SST::Noodle

// EOF
