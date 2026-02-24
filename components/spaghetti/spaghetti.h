//
// _spaghetti_h_
//
// Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_SPAGHETTI_H_
#define _SST_SPAGHETTI_H_

// -- Standard Headers
#include <map>
#include <vector>
#include <queue>
#include <random>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// clang-format off
// -- SST Headers
#include "SST.h"
#include <sst/core/rng/distrib.h>
#include <sst/core/rng/rng.h>
#include <sst/core/rng/mersenne.h>
// clang-format on

namespace SST::Spaghetti{

// -------------------------------------------------------
// SpaghettiEvent
// -------------------------------------------------------
class SpaghettiEvent : public SST::Event{
public:
  /// SpaghettiEvent: standard constructor
  SpaghettiEvent() : SST::Event() {}

  /// SpaghettiEvent: constructor
  SpaghettiEvent(std::vector<uint8_t> d) : SST::Event(), data(d) {}

  /// SpaghettiEvent: destructor
  ~SpaghettiEvent() {}

  /// SpaghettiEvent: retrieve the data
  std::vector<uint8_t> const getData() { return data; }

private:
  std::vector<uint8_t>  data;   ///< SpaghettiEvent: data payload

  /// SpaghettiEvent: serialization method
  void serialize_order(SST::Core::Serialization::serializer& ser) override{
    Event::serialize_order(ser);
    SST_SER(data);
  }

  /// SpaghettiEvent: serialization implementor
  ImplementSerializable(SST::Spaghetti::SpaghettiEvent);

};  // class SpaghettiEvent

// -------------------------------------------------------
// Spaghetti
// -------------------------------------------------------
class Spaghetti final : public SST::Component{
public:
  /// Spaghetti: top-level SST component constructor
  Spaghetti( SST::ComponentId_t id, const SST::Params& params );

  /// Spaghetti: top-level SST destructor
  ~Spaghetti();

  /// Spaghetti: standard SST component 'setup' function
  void setup() override;

  /// Spaghetti: standard SST component 'finish function
  void finish() override;

  /// Spaghetti: standard SST component 'init' function
  void init( unsigned int phase ) override;


  // -------------------------------------------------------
  // Spaghetti Component Registration Data
  // -------------------------------------------------------
  /// Spaghetti: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( Spaghetti,      // component class
                              "spaghetti",    // component library
                              "Spaghetti",    // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "SPAGHETTI SST COMPONENT",
                              COMPONENT_CATEGORY_UNCATEGORIZED )

  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",             "Sets the verbosity level",                       "0" },
    {"numPorts",            "Sets the number of ports",                       "2" },
    {"numMsgs",             "Sets the number of messages per port to inject", "10"},
    {"bytesPerMsg",         "Sets the number of bytes per msg",               "64"},
    {"rngSeed",             "Sets the RNG seed",                              "31337"},
  )

  // -------------------------------------------------------
  // Spaghetti Component Port Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_PORTS(
    {"port%(num_ports)d",
      "Ports which connect to endpoints.",
      {"spaghetti.SpaghettiEvent", ""}
    }
  )

  // -------------------------------------------------------
  // Spaghetti SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // Spaghetti Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS(
    {"LATENCY_PORT_", "Histogram of latency values", "latency", 1},
  )

  // -------------------------------------------------------
  // Spaghetti Component Checkpoint Methods
  // -------------------------------------------------------
  /// Spaghetti: serialization constructor
  Spaghetti() : SST::Component() {}

  /// Spaghetti serialization
  void serialize_order(SST::Core::Serialization::serializer& ser) override {
    SST::Component::serialize_order(ser);
    SST_SER(numPorts);
    SST_SER(numMsgs);
    SST_SER(bytesPerMsg);
    SST_SER(rngSeed);
    SST_SER(numRecv);
    SST_SER(portname);
    SST_SER(linkHandlers);
    SST_SER(localRNG);
    SST_SER(LStat);
  }

  /// Spaghetti: serialization implementations
  ImplementSerializable(SST::Spaghetti::Spaghetti);

private:
  // -- internal handlers
  SST::Output    output;                          ///< SST output handler

  // -- parameters
  uint64_t numPorts;                              ///< number of ports
  uint64_t numMsgs;                               ///< number of messages per clock
  uint64_t bytesPerMsg;                           ///< number of bytes per clock
  uint32_t rngSeed;                               ///< rng seed

  // -- internal state
  uint64_t numRecv;                               ///< number of messages received
  bool injectedData;                              ///< determines whether the messages have been sent
  std::vector<std::string> portname;              ///< port 0 to numPorts names
  std::vector<SST::Link *> linkHandlers;          ///< LinkHandler objects
  SST::RNG::Random* localRNG = 0;                 ///< component local random number generator

  std::vector<Statistic<uint64_t>*> LStat;        ///< Statistics vector.  One entry per port.  Histogram of injection latencies

  // -- private methods
  /// Spaghetti: Message Event Handler
  void handleEvent(SST::Event *ev);

  /// Spaghetti: Sends data to an adjacent link
  void sendData();

};

} // namespace SST::Spaghetti

#endif  // _SST_SPAGHETTI_H_

// EOF
