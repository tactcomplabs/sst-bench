//
// _msg-perf_h_
//
// Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_MSGPERF_H_
#define _SST_MSGPERF_H_

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


namespace SST::MsgPerf{

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
  ImplementSerializable( SST::MsgPerf::nicEvent );
};  // class nicEvent

// -------------------------------------------------------
// MsgPerfAPI
// -------------------------------------------------------
class MsgPerfAPI : public SST::SubComponent{
public:
  SST_ELI_REGISTER_SUBCOMPONENT_API( SST::MsgPerf::MsgPerfAPI )

  /// MsgPerfAPI: constructor
  MsgPerfAPI( ComponentId_t id, Params& params ) : SubComponent( id ) {
  }

  /// MsgPerfAPI: default destructor
  virtual ~MsgPerfAPI() = default;

  /// MsgPerfAPI: registers the event handler with the core
  virtual void setMsgHandler( Event::HandlerBase* handler ) = 0;

  /// MsgPerfAPI: initializes the network
  virtual void init( unsigned int phase ) override = 0;

  /// MsgPerfAPI: setup the network
  virtual void setup() override {}

  /// MsgPerfAPI: send a message on the network
  virtual void send( nicEvent *ev, uint64_t dest ) = 0;

  /// MsgPerfAPI: retrieve the number of destinations
  virtual unsigned getNumDestinations() = 0;

  /// MsgPerfAPI: returns NIC's network address
  virtual SST::Interfaces::SimpleNetwork::nid_t getAddress() = 0;

  /// MsgPerfAPI: return the next possible network address (ring topology)
  virtual uint64_t getNextAddress() = 0;

};  // class MsgPerfAPI

// -------------------------------------------------------
// MsgPerfNIC
// -------------------------------------------------------
class MsgPerfNIC : public MsgPerfAPI {
public:
  // register with the SST Core
  SST_ELI_REGISTER_SUBCOMPONENT( MsgPerfNIC,
                                "msgperf",      // component library
                                "MsgPerfNIC",   // component name
                                SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                                "MSG-PERF SST NIC",
                                SST::MsgPerf::MsgPerfAPI )

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

  // MsgPerfNIC: constructor
  MsgPerfNIC( ComponentId_t id, Params& params );

  /// MsgPerfNIC: destructor
  virtual ~MsgPerfNIC();

  /// MsgPerfNIC: callback to parent on received messages
  virtual void setMsgHandler( Event::HandlerBase* handler ) override;

  /// MsgPerfNIC: init function
  virtual void init( unsigned int phase ) override;

  /// MsgPerfNIC: setup function
  virtual void setup() override;

  /// MsgPerfNIC: send event to the destination id
  virtual void send( nicEvent *ev, uint64_t dest ) override;

  /// MsgPerfNIC: retrieve the number of destinations
  virtual unsigned getNumDestinations() override;

  /// MsgPerfNIC: get the endpoint's network address
  virtual SST::Interfaces::SimpleNetwork::nid_t getAddress() override;

  /// MsgPerfAPI: return the next possible network address (ring topology)
  virtual uint64_t getNextAddress() override;

  /// MsgPerfNIC: clock function
  virtual bool clockTick( Cycle_t cycle );

  /// MsgPerfNIC: callback function for the SimpleNetwork interface
  bool msgNotify( int virtualNetwork );

protected:
  SST::Output output;     ///< MsgPerfNIC: SST output object
  int verbosity;          ///< MsgPerfNIC: verbosity

  TimeConverter* timeConverter;   ///< SST time conversion handler
  SST::Clock::Handler< MsgPerfNIC >* clockHandler;  ///< Clock Handler
  SST::Interfaces::SimpleNetwork *iFace;  ///< MsgPerfNIC: SST network interface

  SST::Event::HandlerBase* msgHandler;    ///< MsgPerfNIC: SST message handler

  bool initBcastSent;   ///< MsgPerfNIC: has the init bcast been sent?

  int numDest;          ///< MsgPerfNIC: number of network destinations

  std::vector<uint64_t> endPoints;  ///< MsgPerfNIC: vector of endpoint IDs

  std::queue< SST::Interfaces::SimpleNetwork::Request* >
    sendQ;  ///< buffered send queue

};  // class MsgPerfNIC

// -------------------------------------------------------
// MsgPerfCPU
// -------------------------------------------------------
class MsgPerfCPU : public SST::Component{
public:
  /// MsgPerfCPU: top-level SST component constructor
  MsgPerfCPU( SST::ComponentId_t id, const SST::Params& params );

  /// MsgPerfCPU: top-level SST component destructor
  ~MsgPerfCPU();

  /// MsgPerfCPU: standard SST component 'setup' function
  void setup() override;

  /// MsgPerfCPU: standard SST component 'finish' function
  void finish() override;

  /// MsgPerfCPU: standard SST component 'init' function
  void init( unsigned int phase ) override;

  /// MsgPerfCPU: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // MsgPerfCPU Component Registration Data
  // -------------------------------------------------------
  /// MsgPerfCPU: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( MsgPerfCPU,     // component class
                              "msgperf",      // component library
                              "MsgPerfCPU",   // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "MSG-PERF SST CPU",
                              COMPONENT_CATEGORY_PROCESSOR )
  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",         "Sets the verbosity level of output",   "0" },
    {"clock",           "Clock for the CPU",                    "1GHz" },
    {"startSize",       "Starting size of the payload (bytes)", "8B" },
    {"endSize",         "Ending size of the payload (bytes)",   "16B" },
    {"stepSize",        "Step size of the payload (bytes)",     "1B" },
    {"iters",           "Number of iterations per step",        "1" },
    {"clockDelay",      "Clock ticks between sends",            "100"},
  )

  // -------------------------------------------------------
  // MsgPerfCPU SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS(
    {"nic", "Network interface", "SST::MsgPerf::MsgPerfNIC"},
  )

  // -------------------------------------------------------
  // MsgPerfCPU Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS(
    {"BitsSent",  "Number of bits sent",  "count",  1},
    {"ByteSize",  "Byte size of payload", "size",   1},
    {"SentClock", "Sent clock cycle",     "cycle",  1},
    {"RecvClock", "Recv clock cycle",     "cycle",  1},
  )

private:
  // -- parameters
  uint64_t startSize;       ///< starting size of the payload
  uint64_t endSize;         ///< ending size of the payload
  uint64_t stepSize;        ///< step size of the payload
  uint64_t iters;           ///< iterations per step
  uint64_t clockDelay;      ///< clock delay between sends

  uint64_t curMsg;          ///< current message ID
  uint64_t msgIter;         ///< msgIter;
  uint64_t clockCount;      ///< clock counter
  uint64_t lastCycle;       ///< last encountered cycle

  unsigned sendStatPtr;     ///< sent current statistic pointer
  unsigned recvStatPtr;     ///< recv current statistic pointer

  SST::Output    output;          ///< SST output handler
  TimeConverter* timeConverter;   ///< SST time conversion handler
  SST::Clock::Handler< MsgPerfCPU >* clockHandler;  ///< Clock Handler
  MsgPerfAPI* Nic;                ///< Network interface controller

  std::vector<uint64_t> steps;    ///< size of each step

  // -- statistics
  Statistic<uint64_t>* BitsSent;
  std::vector<Statistic<uint64_t>*> ByteSize;
  std::vector<Statistic<uint64_t>*> SentClock;
  std::vector<Statistic<uint64_t>*> RecvClock;

  // -- private methods
  /// MsgPerfCPU : setup each simulation step
  void setupSteps();

  /// MsgPerfCPU : send the next message
  void sendMsg();

  /// MsgPerfCPU : handles an incoming network message
  void handleMessage( SST::Event *ev );

};  // class MsgPerfCPU
}   // namespace SST::MsgPerf

#endif  // end _SST_MSGPERF_H_

// EOF
