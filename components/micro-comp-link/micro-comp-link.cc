//
// _micro-comp-link_cc_
//
// Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "micro-comp-link.h"

namespace SST::MicroCompLink{

  //------------------------------------------
  // MicroCompLinkNIC
  //------------------------------------------
  MicroCompLinkNIC::MicroCompLinkNIC( SST::ComponentId_t id, SST::Params& params )
    : MicroCompLinkAPI(id, params){

    uint32_t verbosity = params.find<uint32_t>("verbose", 0);
    output.init(
      "MicroCompLinkNIC[" + getName() + ":@p:@t]: ",
      verbosity, 0, SST::Output::STDOUT );

    const std::string nicClock = params.find< std::string >( "clock", "1GHz" );
    iFace = loadUserSubComponent<SST::Interfaces::SimpleNetwork>(
      "iface", ComponentInfo::SHARE_NONE, 1 );

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
      new SST::Interfaces::SimpleNetwork::Handler<MicroCompLinkNIC>(
        this, &MicroCompLinkNIC::msgNotify ));

    initBcastSent= false;
    msgHandler = nullptr;
  }

  MicroCompLinkNIC::~MicroCompLinkNIC(){
  }

  void MicroCompLinkNIC::setMsgHandler( Event::HandlerBase* handler ){
    msgHandler = handler;
  }

  void MicroCompLinkNIC::init( unsigned int phase ){
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

  void MicroCompLinkNIC::setup(){
    if( msgHandler == nullptr ){
      output.fatal(CALL_INFO,
                   -1,
                   "%s : Error : MicroCompLinkNIC requires a callback-based notification\n",
                   getName().c_str());
    }
  }

  bool MicroCompLinkNIC::msgNotify(int vn){
    SST::Interfaces::SimpleNetwork::Request* req = iFace->recv( 0 );
    if( req != nullptr ){
      nicEvent *ev = static_cast<nicEvent*>(req->takePayload());
      delete req;
      (*msgHandler)(ev);
    }
    return true;
  }

  void MicroCompLinkNIC::send(nicEvent *event, uint64_t destination){
    SST::Interfaces::SimpleNetwork::Request* req =
      new SST::Interfaces::SimpleNetwork::Request();
    req->dest = (SST::Interfaces::SimpleNetwork::nid_t) destination;
    req->src = iFace->getEndpointID();
    req->givePayload( event );
    sendQ.push(req);
  }

  unsigned MicroCompLinkNIC::getNumDestinations(){
    return (unsigned) endPoints.size();
  }

  SST::Interfaces::SimpleNetwork::nid_t MicroCompLinkNIC::getAddress(){
    return iFace->getEndpointID();
  }

  uint64_t MicroCompLinkNIC::getNextAddress(){
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

  bool MicroCompLinkNIC::clockTick(Cycle_t cycle){
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
  // MicroCompLink
  //------------------------------------------
  MicroCompLink::MicroCompLink( SST::ComponentId_t id,
                                const SST::Params& params ) :
    SST::Component( id ),
    timeConverter(nullptr), clockHandler(nullptr), Nic(nullptr){

    const uint32_t Verbosity = params.find< uint32_t >( "verbose", 0 );
    output.init(
      "MicroCompLink[" + getName() + ":@p:@t]: ",
      Verbosity, 0, SST::Output::STDOUT );

    const std::string cpuClock = params.find< std::string >("clock", "1GHz");
    clockHandler  = new SST::Clock::Handler< MicroCompLink>(this,
                                                      &MicroCompLink::clockTick);
    timeConverter = registerClock(cpuClock, clockHandler);

    // Inform SST to wait until we authorize it to exit
    registerAsPrimaryComponent();
    primaryComponentDoNotEndSim();

    // setup the network
    Nic = loadUserSubComponent< MicroCompLinkAPI >( "nic" );
    if( !Nic ){
      output.fatal( CALL_INFO, -1, "Error : no NIC loaded\n" );
    }

    Nic->setMsgHandler(
      new Event::Handler<MicroCompLink>( this,
                                        &MicroCompLink::handleMessage) );

    output.verbose( CALL_INFO, 1, 0, "Initialization of MicroCompLink complete.\n" );
  }

  MicroCompLink::~MicroCompLink(){
  }

  void MicroCompLink::setup(){
    Nic->setup();
  }

  void MicroCompLink::finish(){
  }

  void MicroCompLink::init( unsigned int phase ){
    Nic->init(phase);
  }

  void MicroCompLink::handleMessage( Event *ev ){
    delete ev;
  }

  bool MicroCompLink::clockTick( SST::Cycle_t currentCycle ) {
    primaryComponentOKToEndSim();
    return true;
  }
} // namespace SST::MicroCompLink

// EOF
