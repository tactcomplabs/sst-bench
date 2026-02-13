//
// _micro-comp-link_h_
//
// Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_MICROCOMPLINK_H_
#define _SST_MICROCOMPLINK_H_

// clang-format off
// -- Standard Headers
#include <vector>
#include <queue>
#include <stdio.h>
#include <stdlib.h>
//#include <inttypes.h>
#include <time.h>

// -- SST Headers
#include "SST.h"
// clang-format on

namespace SST::MicroCompLink{

// -------------------------------------------------------
// nicEvent
// -------------------------------------------------------
class nicEvent : public SST::Event{
public:
  /// nicEvent: standard constructor
  explicit nicEvent(std::vector<uint8_t> data)
    : Event(), data(data){}

  /// nicEvent: virtual clone function
  virtual Event *clone(void) override{
    nicEvent *ev = new nicEvent( *this );
    return ev;
  }

private:
  std::vector<uint8_t> data;  ///< nivEvent: data paylod

public:
  /// nicEvent: secondary constructor
  nicEvent() : Event() {
  }

  // nicEvent: retrieve the data payload
  std::vector< uint8_t > getData() {
    return data;
  }

  /// nicEvent: event serializer
  void serialize_order( SST::Core::Serialization::serializer& ser ) override {
    Event::serialize_order(ser);
    ser &data;
  }

  /// nicEvent: implements the NIC serializer
  ImplementSerializable( SST::MicroCompLink::nicEvent );
};  // class nicEvent

// -------------------------------------------------------
// MicroCompLinkAPI
// -------------------------------------------------------
class MicroCompLinkAPI : public SST::SubComponent{
public:
  SST_ELI_REGISTER_SUBCOMPONENT_API( SST::MicroCompLink::MicroCompLinkAPI )

  /// MicroCompLinkAPI: constructor
  MicroCompLinkAPI( ComponentId_t id, Params& params ) : SubComponent( id ) {
  }

  /// MicroCompLinkAPI: default destructor
  virtual ~MicroCompLinkAPI() = default;

  /// MicroCompLinkAPI: registers the event handler with the core
  virtual void setMsgHandler( Event::HandlerBase* handler ) = 0;

  /// MicroCompLinkAPI: initializes the network
  virtual void init( unsigned int phase ) override = 0;

  /// MicroCompLinkAPI: setup the network
  virtual void setup() override {}

  /// MicroCompLinkAPI: send a message on the network
  virtual void send( nicEvent *ev, uint64_t dest ) = 0;

  /// MicroCompLinkAPI: retrieve the number of destinations
  virtual unsigned getNumDestinations() = 0;

  /// MicroCompLinkAPI: returns NIC's network address
  virtual SST::Interfaces::SimpleNetwork::nid_t getAddress() = 0;

  /// MicroCompLinkAPI: return the next possible network address (ring topology)
  virtual uint64_t getNextAddress() = 0;

};  // class MicroCompLinkAPI

// -------------------------------------------------------
// MicroCompLinkNIC
// -------------------------------------------------------
class MicroCompLinkNIC final: public MicroCompLinkAPI {
public:
  // register with the SST Core
  SST_ELI_REGISTER_SUBCOMPONENT( MicroCompLinkNIC,
                                "microcomplink",      // component library
                                "MicroCompLinkNIC",   // component name
                                SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                                "MICRO-COMP-LINK SST NIC",
                                SST::MicroCompLink::MicroCompLinkAPI )

  // register the parameters
  SST_ELI_DOCUMENT_PARAMS(
    { "clock", "Clock frequency of the NIC", "1Ghz" },
    { "port",
      "Port to use, if loaded as an anonymous subcomponent",
      "network" },
    { "verbose", "Verbosity for output (0 = nothing)", "0" }, )

  // register the ports
  SST_ELI_DOCUMENT_PORTS( { "network",
                            "Port to network",
                            { "simpleNetworkExample.nicEvent" } } )

  // register the subcomponent slots
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS( { "iface",
                                         "SimpleNetwork interface to a network",
                                         "SST::Interfaces::SimpleNetwork" } )

  // MicroCompLinkNIC: constructor
  MicroCompLinkNIC( ComponentId_t id, Params& params );

  /// MicroCompLinkNIC: destructor
  virtual ~MicroCompLinkNIC();

  /// MicroCompLinkNIC: callback to parent on received messages
  virtual void setMsgHandler( Event::HandlerBase* handler ) override;

  /// MicroCompLinkNIC: init function
  virtual void init( unsigned int phase ) override;

  /// MicroCompLinkNIC: setup function
  virtual void setup() override;

  /// MicroCompLinkNIC: send event to the destination id
  virtual void send( nicEvent *ev, uint64_t dest ) override;

  /// MicroCompLinkNIC: retrieve the number of destinations
  virtual unsigned getNumDestinations() override;

  /// MicroCompLinkNIC: get the endpoint's network address
  virtual SST::Interfaces::SimpleNetwork::nid_t getAddress() override;

  /// MicroCompLinkAPI: return the next possible network address (ring topology)
  virtual uint64_t getNextAddress() override;

  /// MicroCompLinkNIC: clock function
  virtual bool clockTick( Cycle_t cycle );

  /// MicroCompLinkNIC: callback function for the SimpleNetwork interface
  bool msgNotify( int virtualNetwork );

protected:
  SST::Output output;     ///< MicroCompLinkNIC: SST output object
  int verbosity;          ///< MicroCompLinkNIC: verbosity

  SST::Interfaces::SimpleNetwork *iFace;  ///< MicroCompLinkNIC: SST network interface

  SST::Event::HandlerBase* msgHandler;    ///< MicroCompLinkNIC: SST message handler

  bool initBcastSent;   ///< MicroCompLinkNIC: has the init bcast been sent?

  int numDest;          ///< MicroCompLinkNIC: number of network destinations

  std::vector<uint64_t> endPoints;  ///< MicroCompLinkNIC: vector of endpoint IDs

  std::queue< SST::Interfaces::SimpleNetwork::Request* >
    sendQ;  ///< buffered send queue

};  // class MicroCompLinkNIC

// -------------------------------------------------------
// MicroCompLink
// -------------------------------------------------------
class MicroCompLink : public SST::Component{
public:
  /// MicroCompLink: top-level SST component constructor
  MicroCompLink( SST::ComponentId_t id, const SST::Params& params );

  /// MicroCompLinkCPU: top-level SST component destructor
  ~MicroCompLink();

  /// MicroCompLink: standard SST component 'setup' function
  void setup() override;

  /// MicroCompLink: standard SST component 'finish' function
  void finish() override;

  /// MicroCompLink: standard SST component 'init' function
  void init( unsigned int phase ) override;

  /// MicroCompLink: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // MicroCompLink Component Registration Data
  // -------------------------------------------------------
  /// MicroCompLink: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( MicroCompLink,        // component class
                              "microcomplink",      // component library
                              "MicroCompLink",      // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "MICRO-COMP-LINK SST CPU",
                              COMPONENT_CATEGORY_PROCESSOR )
  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",         "Sets the verbosity level of output",   "0" },
    {"clock",           "Clock for the CPU",                    "1GHz" },
  )

  // -------------------------------------------------------
  // MicroCompLink SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS(
    {"nic", "Network interface", "SST::MicroCompLink::MicroCompLinkNIC"},
  )

  // -------------------------------------------------------
  // MicroCompLink Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS()

private:
  // -- parameters
  SST::Output    output;          ///< SST output handler
  TimeConverter* timeConverter;   ///< SST time conversion handler
  SST::Clock::Handler< MicroCompLink >* clockHandler;  ///< Clock Handler
  MicroCompLinkAPI* Nic;                ///< Network interface controller

  // -- private methods
  /// MicroCompLink : handles an incoming network message
  void handleMessage( SST::Event *ev );

};  // class MicroCompLink
}   // namespace SST::MicroCompLink

#endif  // end _SST_MICROCOMPLINK_H_

// EOF
