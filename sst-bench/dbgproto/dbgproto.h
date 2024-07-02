//
// _DbgProto_h_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_DBGPROTO_H_
#define _SST_DBGPROTO_H_

// -- Standard Headers
#include <vector>
#include <queue>
#include <random>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <time.h>

// -- SST Headers
#include <sst/core/sst_config.h>
#include <sst/core/component.h>
#include <sst/core/event.h>
#include <sst/core/interfaces/simpleNetwork.h>
#include <sst/core/link.h>
#include <sst/core/output.h>
#include <sst/core/statapi/stataccumulator.h>
#include <sst/core/subcomponent.h>
#include <sst/core/timeConverter.h>
#include <sst/core/model/element_python.h>
#include <sst/core/rng/distrib.h>
#include <sst/core/rng/rng.h>
#include <sst/core/rng/mersenne.h>

namespace SST::DbgProto{

// -------------------------------------------------------
// DbgProtoEvent
// -------------------------------------------------------
class DbgProtoEvent : public SST::Event{
public:
  /// DbgProtoEvent : standard constructor
  DbgProtoEvent() : SST::Event() {}

  /// DbgProtoEvent: constructor
  DbgProtoEvent(std::vector<unsigned> d) : SST::Event(), data(d) {}

  /// DbgProtoEvent: destructor
  ~DbgProtoEvent() {}

  /// DbgProtoEvent: retrieve the data
  std::vector<unsigned> const getData() { return data; }

private:
  std::vector<unsigned> data;     ///< DbgProtoEvent: data payload

  /// DbgProtoEvent: serialization method
  void serialize_order(SST::Core::Serialization::serializer& ser) override{
    Event::serialize_order(ser);
    SST_SER(data)
  }

  /// DbgProtoEvent: serialization implementor
  ImplementSerializable(SST::DbgProto::DbgProtoEvent);

};  // class DbgProtoEvent

// -------------------------------------------------------
// DbgProto
// -------------------------------------------------------
class DbgProto : public SST::Component{
public:
  /// DbgProto: top-level SST component constructor
  DbgProto( SST::ComponentId_t id, const SST::Params& params );

  /// DbgProto: top-level SST component destructor
  ~DbgProto();

  /// DbgProto: standard SST component 'setup' function
  void setup() override;

  /// DbgProto: standard SST component 'finish' function
  void finish() override;

  /// DbgProto: standard SST component init function
  void init( unsigned int phase ) override;

  /// DbgProto: standard SST component printStatus
  void printStatus(Output& out) override;

  /// DbgProto: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // DbgProto Component Registration Data
  // -------------------------------------------------------
  /// DbgProto: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( DbgProto,     // component class
                              "dbgproto",   // component library
                              "DbgProto",   // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "DbgProto SST COMPONENT",
                              COMPONENT_CATEGORY_UNCATEGORIZED )

  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",         "Sets the verbosity level of output",   "0" },
    {"numPorts",        "Number of external ports",             "1" },
    {"minData",         "Minimum number of unsigned values",    "1" },
    {"maxData",         "Maximum number of unsigned values",    "2" },
    {"clockDelay",      "Clock delay between sends",            "1" },
    {"clocks",          "Clock cycles to execute",              "1000"},
    {"rngSeed",         "Mersenne RNG Seed",                    "1223"},
    {"clockFreq",       "Clock frequency",                      "1GHz"},
  )

  // -------------------------------------------------------
  // DbgProto Component Port Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_PORTS(
    {"port%(num_ports)d",
      "Ports which connect to endpoints.",
      {"DbgProto.DbgProtoEvent", ""}
    }
  )

  // -------------------------------------------------------
  // DbgProto SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // DbgProto Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS()

  // -------------------------------------------------------
  // DbgProto Component Checkpoint Methods
  // -------------------------------------------------------
  /// DbgProto: serialization constructor
  DbgProto() : SST::Component() {}

  /// DbgProto: serialization
  void serialize_order(SST::Core::Serialization::serializer& ser) override;

  /// DbgProto: serialization implementations
  ImplementSerializable(SST::DbgProto::DbgProto)

private:
  // -- internal handlers
  SST::Output    output;                          ///< SST output handler
  TimeConverter* timeConverter;                   ///< SST time conversion handler
  SST::Clock::HandlerBase* clockHandler;          ///< Clock Handler

  // -- parameters
  unsigned numPorts;                              ///< number of ports to configure
  uint64_t minData;                               ///< minimum number of data elements
  uint64_t maxData;                               ///< maxmium number of data elements
  uint64_t clockDelay;                            ///< clock delay between sends
  uint64_t clocks;                                ///< number of clocks to execute
  uint64_t curCycle;                              ///< current cycle delay

  // -- checkpoint debug markers
  std::string markerMsg;
  uint64_t markerBegin = 0xa5a5a5a5a5a5a5a5ULL;
  uint64_t markerEnd   = 0xf0f0f0f0f0f0f0f0ULL;

  // -- rng objects
  SST::RNG::Random* mersenne;                     ///< mersenne twister object

  std::vector<SST::Link *> linkHandlers;          ///< LinkHandler objects

  // -- private methods
  /// event handler
  void handleEvent(SST::Event *ev);

  /// sends data to adjacent links
  void sendData();

};  // class DbgProto
}   // namespace SST::DbgProto

#endif  // _SST_DBGPROTO_H_

// EOF
