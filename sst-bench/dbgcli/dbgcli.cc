//
// _dbgcli_cc_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "dbgcli.h"
#include "sst/core/kgdbg.h"

namespace SST::DbgCLI{

//------------------------------------------
// DbgCLI
//------------------------------------------
DbgCLI::DbgCLI(SST::ComponentId_t id, const SST::Params& params ) :
  SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr),
  numPorts(1), minData(1), maxData(2), clockDelay(1), clocks(1000),
  curCycle(0) {
  
  kgdbg::spinner("SPINNER");
  const int Verbosity = params.find< int >( "verbose", 0 );
  output.init(
    "DbgCLI[" + getName() + ":@p:@t]: ",
    Verbosity, 0, SST::Output::STDOUT );
  const std::string cpuClock = params.find< std::string >("clockFreq", "1GHz");
  clockHandler  = new SST::Clock::Handler2<DbgCLI,&DbgCLI::clockTick>(this);
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

  // Debug Probe
  probeMode = params.find<int>("probeMode", 0);
  probeStartTime = params.find<int>("probeStartTime",0);
  probeBufferSize = params.find<int>("probeBufferSize", DEFAULT_PROBE_BUFFER_SIZE);
  probePort = params.find<int>("probePort", 0);

  if (probeMode>0) {
    output.verbose(CALL_INFO,1,0,"probeMode=%d\n", probeMode);
    output.verbose(CALL_INFO,1,0,"probeStartTime=%d\n", probeStartTime);
    output.verbose(CALL_INFO,1,0,"probeBufferSize=%d\n", probeBufferSize);
    output.verbose(CALL_INFO,1,0,"probePort=%d\n", probePort);
  }

  // setup the rng
  mersenne = new SST::RNG::MersenneRNG(params.find<unsigned int>("rngSeed", 1223));

  // setup the links
  for( unsigned i=0; i<numPorts; i++ ){
    linkHandlers.push_back(configureLink("port"+std::to_string(i),
                                         new Event::Handler2<DbgCLI,
                                         &DbgCLI::handleEvent>(this)));
  }

  // constructor complete
  output.verbose( CALL_INFO, 5, 0, "Constructor complete\n" );
}

DbgCLI::~DbgCLI(){
  if (probeSocket) delete probeSocket;
}

void DbgCLI::setup(){
}

void DbgCLI::finish(){
}

void DbgCLI::init( unsigned int phase ){
}

void DbgCLI::printStatus( Output& out ){
  assert(false);
}

void DbgCLI::serialize_order(SST::Core::Serialization::serializer& ser){
  SST::Component::serialize_order(ser);
  SST_SER(clockHandler)
  SST_SER(numPorts)
  SST_SER(minData)
  SST_SER(maxData)
  SST_SER(clockDelay)
  SST_SER(clocks)
  SST_SER(curCycle)
  SST_SER(mersenne)
  SST_SER(linkHandlers)
}

void DbgCLI::handle_chkpt_probe_action()
{
  if (!probeMode) return;
  

  if (!probePort) return;
  kgdbg::spinner("PROBE_SPINNER");

  // This should move into sst-core
  if (probeSocket==nullptr) {
    probeSocket = new ProbeSocket(probePort);
    if (probeSocket->create() != ProbeSocket::RESULT::SUCCESS)
      output.fatal( CALL_INFO, -1, "Could not create debug port %d\n", probePort);
    if (probeSocket->connect() != ProbeSocket::RESULT::SUCCESS)
      output.fatal( CALL_INFO, -1, "Could not connect to debug port %d\n", probePort);
  }
  if (probeSocket->connected()) {
    if (probeSocket->cli_handler() != ProbeSocket::RESULT::SUCCESS)
      output.fatal( CALL_INFO, -1, "An error occured on debug port %d\n", probeSocket);
  }
  

  // TODO configure trigger and begin sampling
  // Need to create the  local CDbgControlStateObj which needs to be accessible
  // by the main process.
  // States
  //  SAMPLING
  //  POST_TRIGGER_DELAY
  //  TRIGGER_CHECK
  //  BUFFER_FLUSH

  // Base class handles actions
  serializable_base::handle_chkpt_probe_action();

}

void DbgCLI::handleEvent(SST::Event *ev){
  DbgCLIEvent *cev = static_cast<DbgCLIEvent*>(ev);
  output.verbose(CALL_INFO, 5, 0,
                 "%s: received %zu unsigned values\n",
                 getName().c_str(),
                 cev->getData().size());
  delete ev;
}

void DbgCLI::sendData(){
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
    DbgCLIEvent *ev = new DbgCLIEvent(data);
    linkHandlers[i]->send(ev);
  }
}

bool DbgCLI::clockTick( SST::Cycle_t currentCycle ){

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

} // namespace SST::DbgCLI

// EOF
