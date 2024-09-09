//
// _msg-perf_cc_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "msg-perf.h"

namespace SST::MsgPerf{

  //------------------------------------------
  // MsgPerfNIC
  //------------------------------------------
  MsgPerfNIC::MsgPerfNIC( SST::ComponentId_t id, SST::Params& params )
    : MsgPerfAPI(id, params), timeConverter(nullptr), clockHandler(nullptr),
      iFace(nullptr), msgHandler(nullptr), initBcastSent(false), numDest(0) {

    int verbosity = params.find<int>("verbose", 0);
    output.init(
      "MsgPerfNIC[" + getName() + ":@p:@t]: ",
      verbosity, 0, SST::Output::STDOUT );

    const std::string nicClock = params.find< std::string >( "clock", "1GHz" );
    iFace = loadUserSubComponent<SST::Interfaces::SimpleNetwork>(
      "iface", ComponentInfo::SHARE_NONE, 1 );

    clockHandler  = new SST::Clock::Handler< MsgPerfNIC >(this,
                                                      &MsgPerfNIC::clockTick);
    timeConverter = registerClock(nicClock, clockHandler);

    if( !iFace ){
      // load the anonymous nic
      Params netparams;
      netparams.insert( "port_name",
                        params.find< std::string >( "port", "network" ) );
      netparams.insert( "in_buf_size", "256B" );
      netparams.insert( "out_buf_size", "256B" );
      netparams.insert( "link_bw", "40GiB/s" );
      iFace = loadAnonymousSubComponent< SST::Interfaces::SimpleNetwork >(
        "merlin.linkcontrol",
        "iface",
        0,
        ComponentInfo::SHARE_PORTS | ComponentInfo::INSERT_STATS,
        netparams,
        1 );
    }

    iFace->setNotifyOnReceive(
      new SST::Interfaces::SimpleNetwork::Handler<MsgPerfNIC>(
        this, &MsgPerfNIC::msgNotify ));
  }

  MsgPerfNIC::~MsgPerfNIC(){
  }

  void MsgPerfNIC::setMsgHandler( Event::HandlerBase* handler ){
    msgHandler = handler;
  }

  void MsgPerfNIC::init( unsigned int phase ){
    iFace->init(phase);

    // send the init data
    if( iFace->isNetworkInitialized() ){
      if( !initBcastSent ){
        initBcastSent = true;

        std::vector<uint8_t> dummy;
        uint64_t id = (uint64_t)(iFace->getEndpointID());
        output.verbose(CALL_INFO, 10, 0,
                       "Broadcasting endpoint id=%" PRIu64 "\n",
                       id);
        dummy.push_back( (uint8_t)(id&0b11111111) );
        dummy.push_back( (uint8_t)((id>>8)&0b11111111) );
        dummy.push_back( (uint8_t)((id>>16)&0b11111111) );
        dummy.push_back( (uint8_t)((id>>24)&0b11111111) );
        dummy.push_back( (uint8_t)((id>>32)&0b11111111) );
        dummy.push_back( (uint8_t)((id>>40)&0b11111111) );
        dummy.push_back( (uint8_t)((id>>48)&0b11111111) );
        dummy.push_back( (uint8_t)((id>>56)&0b11111111) );

        nicEvent *ev = new nicEvent(dummy);
        SST::Interfaces::SimpleNetwork::Request* req =
          new SST::Interfaces::SimpleNetwork::Request();
        req->dest = SST::Interfaces::SimpleNetwork::INIT_BROADCAST_ADDR;
        req->src = iFace->getEndpointID();
        req->givePayload(ev);
        iFace->sendUntimedData(req);
      }
    }

    // receive all the init data
    while( SST::Interfaces::SimpleNetwork::Request* req =
           iFace->recvUntimedData() ){
      nicEvent *ev = static_cast<nicEvent *>(req->takePayload());

      // decode the endpoint id
      uint64_t endP = 0x00ull;
      std::vector<uint8_t> data = ev->getData();
      unsigned shift = 0;
      for( unsigned i=0; i<data.size(); i++ ){
        endP |= ((uint64_t)(data[i]) << shift);
        shift += 8;
      }
      output.verbose(CALL_INFO, 10, 0,
                     "Receiving endpoint id=%" PRIu64 "\n",
                     endP);

      endPoints.push_back(endP);
    }

    std::sort(endPoints.begin(), endPoints.end());

    // sanity check the number of endpoints
    if( iFace->isNetworkInitialized() ){
      if( !initBcastSent ){
        if( endPoints.size() == 0 ){
          output.fatal(CALL_INFO,
                       -1,
                       "%s : Error : minimum number of endpoints must be 2\n",
                       getName().c_str());
        }
      }
    }
  }

  void MsgPerfNIC::setup(){
    if( msgHandler == nullptr ){
      output.fatal(CALL_INFO,
                   -1,
                   "%s : Error : MsgPerfNIC requires a callback-based notification\n",
                   getName().c_str());
    }
  }

  bool MsgPerfNIC::msgNotify(int vn){
    SST::Interfaces::SimpleNetwork::Request* req = iFace->recv( 0 );
    if( req != nullptr ){
      nicEvent *ev = static_cast<nicEvent*>(req->takePayload());
      delete req;
      (*msgHandler)(ev);
    }
    return true;
  }

  void MsgPerfNIC::send(nicEvent *event, uint64_t destination){
    SST::Interfaces::SimpleNetwork::Request* req =
      new SST::Interfaces::SimpleNetwork::Request();
    req->dest = destination;
    req->src = iFace->getEndpointID();
    req->givePayload( event );
    sendQ.push(req);
  }

  unsigned MsgPerfNIC::getNumDestinations(){
    return endPoints.size();
  }

  SST::Interfaces::SimpleNetwork::nid_t MsgPerfNIC::getAddress(){
    return iFace->getEndpointID();
  }

  uint64_t MsgPerfNIC::getNextAddress(){
    uint64_t myAddr = (uint64_t)(getAddress());
    for( unsigned i=0; i<endPoints.size(); i++ ){
      if( endPoints[i] == myAddr ){
        if( (i+1) <= (endPoints.size()-1) ){
          return endPoints[i+1];
        }else{
          return endPoints[0];
        }
      }
    }
    return 0;
  }

  bool MsgPerfNIC::clockTick(Cycle_t cycle){
    while( !sendQ.empty() ){
      if( iFace->spaceToSend(0,
                             (int)(sendQ.front()->size_in_bits)) &&
          iFace->send(sendQ.front(), 0) ){
        sendQ.pop();
      }else{
        break;
      }
    }
    return false;
  }

  //------------------------------------------
  // MsgPerfCPU
  //------------------------------------------
  MsgPerfCPU::MsgPerfCPU( SST::ComponentId_t id, const SST::Params& params ) :
    SST::Component( id ),
    startSize(8), endSize(16), stepSize(8), iters(1), clockDelay(100),
    curMsg(0), msgIter(0), clockCount(0), lastCycle(0),
    sendStatPtr(0), recvStatPtr(0),
    timeConverter(nullptr), clockHandler(nullptr), Nic(nullptr){

    const int Verbosity = params.find< int >( "verbose", 0 );
    output.init(
      "MsgPerfCPU[" + getName() + ":@p:@t]: ",
      Verbosity, 0, SST::Output::STDOUT );

    const std::string cpuClock = params.find< std::string >("clock", "1GHz");
    clockHandler  = new SST::Clock::Handler< MsgPerfCPU >(this,
                                                      &MsgPerfCPU::clockTick);
    timeConverter = registerClock(cpuClock, clockHandler);

    // Inform SST to wait until we authorize it to exit
    registerAsPrimaryComponent();
    primaryComponentDoNotEndSim();

    // read all the remaining parameters
    startSize = params.find<SST::UnitAlgebra>("startSize", "8B").getRoundedValue();
    endSize = params.find<SST::UnitAlgebra>("endSize", "16B").getRoundedValue();
    stepSize = params.find<SST::UnitAlgebra>("stepSize", "1B").getRoundedValue();
    iters = params.find<uint64_t>("iters", 1);
    clockDelay = params.find<uint64_t>("clockDelay", 100);

    // error checking
    if( endSize <= startSize ){
      output.fatal(
        CALL_INFO, -1, "Error : endSize <= startSize" );
    }

    // setup the network
    Nic = loadUserSubComponent< MsgPerfAPI >( "nic" );
    if( !Nic ){
      output.fatal( CALL_INFO, -1, "Error : no NIC loaded\n" );
    }

    Nic->setMsgHandler(
      new Event::Handler<MsgPerfCPU>( this,
                                      &MsgPerfCPU::handleMessage) );

    // setup the steps
    setupSteps();

    output.verbose( CALL_INFO, 1, 0, "Initialization of MsgPerfCPU complete.\n" );
  }

  MsgPerfCPU::~MsgPerfCPU(){
  }

  void MsgPerfCPU::setup(){
    Nic->setup();
  }

  void MsgPerfCPU::finish(){
  }

  void MsgPerfCPU::init( unsigned int phase ){
    Nic->init(phase);
  }

  void MsgPerfCPU::handleMessage( Event *ev ){
    delete ev;
    // TODO: record statistics
    //RecvClock[recvStatPtr]->addData((uint64_t)(currentCycle));
    recvStatPtr++;
  }

  void MsgPerfCPU::setupSteps(){
    uint64_t cur = startSize;
    do{
      steps.push_back(cur);
      cur += stepSize;
    }while( cur <= endSize );

    // setup all the statistics
    BitsSent = registerStatistic<uint64_t>("BitsSent");
    for( unsigned i=0; i<steps.size(); i++ ){
      for( uint64_t j=0; j<iters; j++ ){
        // step i; iter j statistics
        std::string post = std::to_string(steps[i]) + "_" + std::to_string(j);
        ByteSize.push_back(
          registerStatistic<uint64_t>(
            "ByteSize", post));
        SentClock.push_back(
          registerStatistic<uint64_t>(
            "SentClock", post));
        RecvClock.push_back(
          registerStatistic<uint64_t>(
            "RecvClock", post));
      }
    }

    output.verbose( CALL_INFO,
                    2,
                    0,
                    "Setup %ld steps with %" PRIu64 " iterations each; %" PRIu64 " total sends\n",
                    steps.size(), iters, (uint64_t)(steps.size()) * iters );
  }

  void MsgPerfCPU::sendMsg(){
    // step 1: build the payload
    std::vector<uint8_t> payload;
    for( uint64_t i=0; i < steps[curMsg]; i++ ){
      payload.push_back((uint8_t)(0b11111111));
    }

    // step 2: determine where to send it
    uint64_t dest = Nic->getNextAddress();

    // step 3: send the payload
    nicEvent *ev = new nicEvent(payload);
    output.verbose( CALL_INFO, 5, 0,
                    "Sending message of %d bytes from %" PRIu64 " to %" PRIu64 "\n",
                    (int)(payload.size()),
                    (uint64_t)(Nic->getAddress()),
                    dest );
    Nic->send(ev,dest);

    BitsSent->addData(payload.size()*8);

    msgIter++;
    if( msgIter == iters ){
      curMsg++;
      msgIter = 0;
    }
  }

  bool MsgPerfCPU::clockTick( SST::Cycle_t currentCycle ) {
    // see if we're ready to finish
    if( curMsg == (uint64_t)(steps.size()) ){
      output.verbose( CALL_INFO, 1, 0,
                      "%s ready to end simulation\n",
                      getName().c_str());
      primaryComponentOKToEndSim();
      return true;
    }

    // -- begin main event loop
    clockCount += (uint64_t)(currentCycle) - lastCycle;
    lastCycle = (uint64_t)(currentCycle);
    if( clockCount >= clockDelay ){
      ByteSize[sendStatPtr]->addData(steps[curMsg]);
      SentClock[sendStatPtr]->addData((uint64_t)(currentCycle));
      sendMsg();
      sendStatPtr++;
      clockCount = 0;
    }
    // -- end main event loop

    return false;
  }
}

// EOF
