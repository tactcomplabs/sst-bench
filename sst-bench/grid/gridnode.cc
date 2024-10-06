//
// _gridnode_cc_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "gridnode.h"
#include "kgdbg.h"

namespace SST::GridNode{

//------------------------------------------
// GridNode
//------------------------------------------
GridNode::GridNode(SST::ComponentId_t id, const SST::Params& params ) :
  SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr),
  numPorts(1), minData(1), maxData(2), clockDelay(1), clocks(1000),
  curCycle(0) {
  
  kgdbg::spinner("GRIDSPINNER");

  const int Verbosity = params.find< int >( "verbose", 0 );
  output.init(
    "GridNode[" + getName() + ":@p:@t]: ",
    Verbosity, 0, SST::Output::STDOUT );
  const std::string cpuClock = params.find< std::string >("clockFreq", "1GHz");
  clockHandler  = new SST::Clock::Handler2<GridNode,&GridNode::clockTick>(this);
  timeConverter = registerClock(cpuClock, clockHandler);
  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();

  // read the rest of the parameters
  numBytes = params.find<SST::UnitAlgebra>("numBytes", "64KB").getRoundedValue();
  numPorts = params.find<unsigned>("numPorts", 1);
  minData = params.find<uint64_t>("minData", 10);
  maxData = params.find<uint64_t>("maxData", 65536);
  clockDelay = params.find<uint64_t>("clockDelay", 1);
  clocks = params.find<uint64_t>("clocks", 1000);
  baseSeed = params.find<unsigned>("baseSeed", "1223");

  // sanity check the params
  if (minData < 10) {
    output.verbose(CALL_INFO, 1, 0, 
    "Warning: User specified minData < 10. Setting to 10\n");
    minData = 10;
  }
  if( maxData < minData ){
    output.fatal(CALL_INFO, -1,
                 "%s : maxData < minData\n",
                 getName().c_str());
  }

  // setup the port links and their random generators
  assert(numPorts==8); // TODO generalize this
  portname.resize(numPorts);
  for( unsigned i=0; i<numPorts; i++ ){
    portname[i] = "port" + std::to_string(i);
    linkHandlers.push_back(configureLink("port"+std::to_string(i),
                                         new Event::Handler2<GridNode,
                                         &GridNode::handleEvent>(this)));
    // TODO unique seed for each port matching recievers seed with corresponding senders.
    // send: up=0, down=1, left=2, right=3
    // rcv:  up=4, down=5, left=6, right=7
    rng.insert( {portname[i], new SST::RNG::MersenneRNG(params.find<unsigned int>("rngSeed",baseSeed))} );

  }

  // constructor complete
  output.verbose( CALL_INFO, 5, 0, "Constructor complete\n" );
}

GridNode::~GridNode(){
  for (unsigned i=0;i<numPorts; i++) {
    if (rng[portname[i]]) 
      delete rng[portname[i]];
  }
}

void GridNode::setup(){
}

void GridNode::finish(){
}

void GridNode::init( unsigned int phase ){
  if( phase == 0 ){
    // setup the initial data
    output.verbose(CALL_INFO, 5, 0,
                   "%s: initializing internal data at init phase=0\n",
                   getName().c_str());
    for( uint64_t i = 0; i < (numBytes/4ull); i++ ){
      state.push_back( (unsigned)(i) + baseSeed );
    }
  }
}

void GridNode::printStatus( Output& out ){
}

void GridNode::serialize_order(SST::Core::Serialization::serializer& ser){
  SST::Component::serialize_order(ser);
  SST_SER(clockHandler)
  SST_SER(numBytes)
  SST_SER(numPorts)
  SST_SER(minData)
  SST_SER(maxData)
  SST_SER(clockDelay)
  SST_SER(clocks)
  SST_SER(baseSeed)
  SST_SER(state)
  SST_SER(curCycle)
  SST_SER(portname)
  SST_SER(rng)
  SST_SER(linkHandlers)
}

void GridNode::handleEvent(SST::Event *ev){
  GridNodeEvent *cev = static_cast<GridNodeEvent*>(ev);
  auto data = cev->getData();
  output.verbose(CALL_INFO, 5, 0,
                 "%s: received %zu unsigned values\n",
                 getName().c_str(),
                 data.size());
  // Inbound data sequence
  // [0] sending port number
  // [1] r
  // [2:(r-1)] random data
  // Check the incoming data

  unsigned send_port = data[0];
  assert(send_port < (portname.size()/2)); // TODO unrestrict bidirectional links
  unsigned rcv_port = neighbor(send_port);
  auto portRNG = rng[portname[rcv_port]];
  unsigned range = maxData - minData + 1;
  unsigned r = portRNG->generateNextUInt32() % range + minData;
  if (r != data.size()) {
    output.fatal(CALL_INFO, -1,
                  "%s expected data size %" PRIu32 " does not match actual size %" PRIu64 "\n",
                  getName().c_str(), r, data.size());
  }
  if (r != data[1]) {
    output.fatal(CALL_INFO, -1,
              "%s expected data[0] %" PRIu32 " does not match actual %" PRIu32 "\n",
              getName().c_str(), r, data[0]);
  }
  for (unsigned i=2; i<r; i++){
    unsigned d = (unsigned)portRNG->generateNextUInt32();
    if ( d != data[i] ) {
      output.fatal(CALL_INFO, -1,
          "%s expected data[%" PRIu32 "] %" PRIu32 " does not match actual %" PRIu32 "\n",
          getName().c_str(), i, d, data[i]);
    }
  }
  
  delete ev;
}

void GridNode::sendData(){
  // Iterate over sending ports.
  // Treating links as unidirectional so the recieve port RNG tracks the send port.
  // TODO: create 2 RNG's per port, one for send, one for recieve
  for( unsigned port=0; port<(numPorts/2); port++ ){
    // generate a new payload
    std::vector<unsigned> data;
    unsigned range = maxData - minData + 1;
    unsigned r = rng[portname[port]]->generateNextUInt32() % range + minData;
    // Outbound data sequence
    // [0] sending port number
    // [1] number of ints
    // [2:r-1] random data
    data.push_back(port);
    data.push_back(r);
    for( unsigned i=2; i<r; i++ ){
      data.push_back((unsigned)(rng[portname[port]]->generateNextUInt32()));
    }
    output.verbose(CALL_INFO, 5, 0,
                   "%s: sending %zu unsigned values on link %d\n",
                   getName().c_str(),
                   data.size(), port);
    GridNodeEvent *ev = new GridNodeEvent(data);
    linkHandlers[port]->send(ev);
  }
}

unsigned GridNode::neighbor(unsigned n)
{
  // send: up=0, down=1, left=2, right=3
  // rcv:  up=4, down=5, left=6, right=7
  assert(n < numPorts/2); //TODO bidirectional links
  switch (n) {
    case 0:
      return 5;
    case 1:
      return 4;
    case 2:
      return 7;
    case 3:
      return 6;
    case 4:
      return 1;
    case 5:
      return 0;
    case 6:
      return 3;
    case 7:
      return 2;
    default:
      output.fatal(CALL_INFO, -1, "invalid port number\n");
  }
  assert(false);
  return 8; // invalid
}

bool GridNode::clockTick( SST::Cycle_t currentCycle ){

  // sanity check the array
  for( uint64_t i = 0; i < (numBytes/4ull); i++ ){
    if( state[i] != ((unsigned)(i) + baseSeed) ){
      // found a mismatch
      output.fatal( CALL_INFO, -1,
                    "Error : found a mismatch data element: element %" PRIu64 " was %d and should have been %d\n",
                    i, state[i], ((unsigned)(i) + baseSeed));
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

} // namespace SST::GridNode

// EOF
