//
// _flood_h_
//
// Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_FLOOD_H_
#define _SST_FLOOD_H_

// -- Standard Headers
#include <vector>
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

#define _U641GB_  0x8000000ull

namespace SST::Flood{

// -------------------------------------------------------
// FloodEvent
// -------------------------------------------------------
class FloodEvent : public SST::Event{
public:
  /// FloodEvent: standard constructor
  FloodEvent() : SST::Event() {}

  /// FloodEvent: constructor
  FloodEvent(std::vector<uint64_t> d) : SST::Event(), data(d) {}

  /// NoodleEvent: destructor
  ~FloodEvent() {}

  /// NoodleEvent: retrieve the data
  std::vector<uint64_t> const getData() { return data; }

private:
  std::vector<uint64_t> data;   ///< FloodEvent: data payload

  /// FloodEvent: serialization method
  void serialize_order(SST::Core::Serialization::serializer& ser) override{
    Event::serialize_order(ser);
    SST_SER(data);
  }

  /// FloodEvent: serialization implementor
  ImplementSerializable(SST::Flood::FloodEvent);

};  // class FloodEvent

// -------------------------------------------------------
// Flood
// -------------------------------------------------------
class Flood final : public SST::Component{
public:
  /// Flood: top-level SST component constructor
  Flood( SST::ComponentId_t id, const SST::Params& params );

  /// Flood: top-level SST destructor
  ~Flood();

  /// Flood: standard SST component 'setup' function
  void setup() override;

  /// Flood: standard SST component 'finish' function
  void finish() override;

  /// Flood: standard SST component 'init' function
  void init( unsigned int phase ) override;

  /// Flood: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // Flood Component Registration Data
  // -------------------------------------------------------
  /// Flood: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( Flood,      // component class
                              "flood",    // component library
                              "Flood",    // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "FLOOD SST COMPONENT",
                              COMPONENT_CATEGORY_UNCATEGORIZED )

  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",             "Sets the verbosity level",                   "0" },
    {"clockFreq",           "Sets the clock frequency",                   "1GHz" },
    {"numPorts",            "Sets the number of ports",                   "2" },
    {"gigabytePerMsg",      "Sets the number of GBs per message",         "8" },
    {"portsPerClock",       "Sets the number of ports to send per clock", "1" },
    {"clocks",              "Sets the number of clocks to execute",       "10000"},
    {"rngSeed",             "Sets the RNG seed",                          "31337"},
    {"hubComp",             "Sets whether this component is the hub",     "false"},
  )

  // -------------------------------------------------------
  // Flood Component Port Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_PORTS(
    {"port%(num_ports)d",
      "Ports which connect to endpoints.",
      {"flood.FloodEvent", ""}
    }
  )

  // -------------------------------------------------------
  // Flood SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // Flood Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS()

  // -------------------------------------------------------
  // Flood Component Checkpoint Methods
  // -------------------------------------------------------
  /// Flood: serialization constructor
  Flood() : SST::Component() {}

  /// Flood: serialization
  void serialize_order(SST::Core::Serialization::serializer& ser) override {
    SST::Component::serialize_order(ser);
    SST_SER(clockHandler);
    SST_SER(numPorts);
    SST_SER(msgsPerClock);
    SST_SER(gbPerMsg);
    SST_SER(portsPerClock);
    SST_SER(clocks);
    SST_SER(rngSeed);
    SST_SER(hubComp);
    SST_SER(portname);
    SST_SER(linkHandlers);
    SST_SER(localRNG);
  }

  /// Flood: serialization implementations
  ImplementSerializable(SST::Flood::Flood);

private:
  // -- internal handlers
  SST::Output    output;                          ///< SST output handler
  TimeConverter* timeConverter;                   ///< SST time conversion handler
  SST::Clock::HandlerBase* clockHandler;          ///< Clock Handler

  // -- parameters
  uint64_t numPorts;                              ///< number of ports
  uint64_t msgsPerClock;                          ///< number of messages per clock
  uint64_t gbPerMsg;                              ///< number of GB per message
  uint64_t portsPerClock;                         ///< number of ports per clock to send data across
  uint64_t clocks;                                ///< number of clocks to execute
  uint32_t rngSeed;                               ///< rng seed
  bool hubComp;                                   ///< hub component

  // -- internal state
  std::vector<std::string> portname;              ///< port 0 to numPorts names
  std::vector<SST::Link *> linkHandlers;          ///< LinkHandler objects
  SST::RNG::Random* localRNG = 0;                 ///< component local random number generator

  std::vector<uint64_t> packet;

  // -- private methods
  /// Flood: Message Event Handler
  void handleEvent(SST::Event *ev);

  /// Flood: Sends data to an adjacent link
  void sendData();

};  // class Flood

} // namespace SST::Flood

#endif // _SST_FLOOD_H_

// EOF
