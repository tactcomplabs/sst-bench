//
// _noodle_h_
//
// Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_NOODLE_H_
#define _SST_NOODLE_H_

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

namespace SST::Noodle{

// -------------------------------------------------------
// NoodleEvent
// -------------------------------------------------------
class NoodleEvent : public SST::Event{
public:
  /// NoodleEvent: standard constructor
  NoodleEvent() : SST::Event() {}

  /// NoodleEvent: constructor
  NoodleEvent(std::vector<uint8_t> d) : SST::Event(), data(d) {}

  /// NoodleEvent: destructor
  ~NoodleEvent() {}

  /// NoodleEvent: retrieve the data
  std::vector<uint8_t> const getData() { return data; }

private:
  std::vector<uint8_t>  data;   ///< NoodleEvent: data payload

  /// NoodleEvent: serialization method
  void serialize_order(SST::Core::Serialization::serializer& ser) override{
    Event::serialize_order(ser);
    SST_SER(data);
  }

  /// NoodleEvent: serialization implementor
  ImplementSerializable(SST::Noodle::NoodleEvent);

};  // class NoodleEvent


// -------------------------------------------------------
// Noodle
// -------------------------------------------------------
class Noodle final : public SST::Component{
public:
  /// Noodle: top-level SST component constructor
  Noodle( SST::ComponentId_t id, const SST::Params& params );

  /// Noodle: top-level SST destructor
  ~Noodle();

  /// Noodle: standard SST component 'setup' function
  void setup() override;

  /// Noodle: standard SST component 'finish' function
  void finish() override;

  /// Noodle: standard SST component 'init' function
  void init( unsigned int phase ) override;

  /// Noodle: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // Noodle Component Registration Data
  // -------------------------------------------------------
  /// Noodle: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( Noodle,     // component class
                              "noodle",       // component library
                              "Noodle",   // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "NOODLE SST COMPONENT",
                              COMPONENT_CATEGORY_UNCATEGORIZED )

  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",             "Sets the verbosity level",                   "0" },
    {"clockFreq",           "Sets the clock frequency",                   "1GHz" },
    {"numPorts",            "Sets the number of ports",                   "2" },
    {"msgsPerClock",        "Sets the number of messages sent per clock", "8" },
    {"bytesPerClock",       "Sets the number of bytes per clock",         "8" },
    {"portsPerClock",       "Sets the number of ports to send per clock", "1" },
    {"clocks",              "Sets the number of clocks to execute",       "10000"},
    {"rngSeed",             "Sets the RNG seed",                          "31337"},
  )

  // -------------------------------------------------------
  // Noodle Component Port Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_PORTS(
    {"port%(num_ports)d",
      "Ports which connect to endpoints.",
      {"noodle.NoodleEvent", ""}
    }
  )

  // -------------------------------------------------------
  // Noodle SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // Noodle Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS()

  // -------------------------------------------------------
  // Noodle Component Checkpoint Methods
  // -------------------------------------------------------
  /// Noodle: serialization constructor
  Noodle() : SST::Component() {}

  /// Noodle: serialization
  void serialize_order(SST::Core::Serialization::serializer& ser) override {
    SST::Component::serialize_order(ser);
    SST_SER(clockHandler);
    SST_SER(numPorts);
    SST_SER(msgsPerClock);
    SST_SER(bytesPerClock);
    SST_SER(portsPerClock);
    SST_SER(clocks);
    SST_SER(rngSeed);
    SST_SER(portname);
    SST_SER(linkHandlers);
    SST_SER(localRNG);
  }

  /// Noodle: serialization implementations
  ImplementSerializable(SST::Noodle::Noodle)

private:
  // -- internal handlers
  SST::Output    output;                          ///< SST output handler
  TimeConverter* timeConverter;                   ///< SST time conversion handler
  SST::Clock::HandlerBase* clockHandler;          ///< Clock Handler

  // -- parameters
  uint64_t numPorts;                              ///< number of ports
  uint64_t msgsPerClock;                          ///< number of messages per clock
  uint64_t bytesPerClock;                         ///< number of bytes per clock
  uint64_t portsPerClock;                         ///< number of ports per clock to send data across
  uint64_t clocks;                                ///< number of clocks to execute
  uint32_t rngSeed;                               ///< rng seed

  // -- internal state
  std::vector<std::string> portname;              ///< port 0 to numPorts names
  std::vector<SST::Link *> linkHandlers;          ///< LinkHandler objects
  SST::RNG::Random* localRNG = 0;                 ///< component local random number generator

  // -- private methods
  /// Noodle: Message Event Handler
  void handleEvent(SST::Event *ev);

  /// Noodle: Sends data to an adjacent link
  void sendData();

};  // class Noodle

} // namespace SST::Noodle

#endif // _SST_NOODLE_H_

// EOF
