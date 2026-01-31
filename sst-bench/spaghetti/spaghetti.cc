//
// _spaghetti_cc_
//
// Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "spaghetti.h"

namespace SST::Spaghetti{

//------------------------------------------
// Noodle
//------------------------------------------
Spaghetti::Spaghetti(SST::ComponentId_t id, const SST::Params& params ) :
  SST::Component( id ), numPorts(2), numMsgs(10), bytesPerMsg(64),
  rngSeed(31337), numRecv(0), injectedData(false) {

  uint32_t Verbosity = params.find<uint32_t>("verbose", 0);
  output.init(
    "Spaghetti[" + getName() + ":@p:@t]: ",
    Verbosity, 0, SST::Output::STDOUT );

  // register our component
  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();

  // read the rest of the parameters
  numPorts = params.find<uint64_t>("numPorts", 2);
  numMsgs = params.find<uint64_t>("numMsgs", 10);
  bytesPerMsg = params.find<uint64_t>("bytesPerMsg", 64);
  rngSeed = params.find<uint32_t>("rngSeed", 31337);

  // setup the port handlers
  portname.resize(numPorts);
  linkHandlers.resize(numPorts);
  for( uint64_t i = 0; i<numPorts; i++ ){
    portname[i] = "port" + std::to_string(i);
    linkHandlers[i] = configureLink(portname[i],
                                    new Event::Handler2<Spaghetti,
                                    &Spaghetti::handleEvent>(this));
  }

  // setup the local rand number generator
  localRNG = new SST::RNG::MersenneRNG(uint32_t(id) + rngSeed);

  // constructor complete
  output.verbose( CALL_INFO, 5, 0, "Constructor complete\n" );
}

Spaghetti::~Spaghetti(){
  if( localRNG ) delete localRNG;
}

void Spaghetti::setup(){
  if( !injectedData ){
    sendData();
    injectedData = true;
  }
  output.verbose( CALL_INFO, 5, 0, "Setup complete\n" );
}

void Spaghetti::finish(){
  output.verbose( CALL_INFO, 5, 0, "Finish complete\n" );
}

void Spaghetti::init( unsigned int phase ){
  output.verbose( CALL_INFO, 5, 0, "Init Phase=%d\n", 2 );
}

void Spaghetti::handleEvent(SST::Event *ev){
  SpaghettiEvent *se = static_cast<SpaghettiEvent*>(ev);
  auto data = se->getData();
  output.verbose(CALL_INFO, 5, 0,
                 "%s: received %zu bytes\n",
                 getName().c_str(),
                 data.size());
  delete ev;

  // check for completion status
  numRecv+=1;
  if( numRecv == (numMsgs*numPorts) ){
    primaryComponentOKToEndSim();
  }
}

void Spaghetti::sendData(){
  output.verbose(CALL_INFO, 5, 0, "sendData()\n");
  for( unsigned i=0; i<numPorts; i++ ){
    for( unsigned j=0; j<numMsgs; j++ ){
      // build a packet
      std::vector<uint8_t> packet;
      packet.resize(bytesPerMsg);
      for( uint64_t m = 0x00ull; m<bytesPerMsg; m++ ){
        packet[m] = ((uint8_t)(localRNG->generateNextUInt32() & 0b11111111));
      }

      // create the packet
      SpaghettiEvent *se = new SpaghettiEvent(packet);

      // create random time bases and delays using our localRNG
      // time bases are restricted to three bits of precision, aka 7MHz
      // delays are restrict to 8 bits of precision. 
      // 0 MHz is illegal
      uint32_t freq = localRNG->generateNextUInt32() & 0b111;
      if (freq==0) {
        std::cout << "HIT 0" << std::endl;
        // freq=1;
      }
      TimeConverter tc = getTimeConverter(std::to_string(freq) + "MHz");
      SimTime_t delay = (SimTime_t)(localRNG->generateNextUInt32() & 0b11111111);
      linkHandlers[i]->send(delay, tc, se);

      output.verbose(CALL_INFO, 5, 0,
                     "%s: injected %zu byte message into port = %s\n",
                     getName().c_str(),
                     packet.size(),
                     portname[i].c_str());
    }
  }
}

} // namespace SST::Spaghetti

// EOF
