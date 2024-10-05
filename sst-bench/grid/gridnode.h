//
// _gridnode_h_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_GRIDNODE_H_
#define _SST_GRIDNODE_H_

// -- Standard Headers
#include <map>
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

namespace SST::GridNode{

// -------------------------------------------------------
// GridNodeEvent
// -------------------------------------------------------
class GridNodeEvent : public SST::Event{
public:
  /// GridNodeEvent : standard constructor
  GridNodeEvent() : SST::Event() {}

  /// GridNodeEvent: constructor
  GridNodeEvent(std::vector<unsigned> d) : SST::Event(), data(d) {}

  /// GridNodeEvent: destructor
  ~GridNodeEvent() {}

  /// GridNodeEvent: retrieve the data
  std::vector<unsigned> const getData() { return data; }

private:
  std::vector<unsigned> data;     ///< GridNodeEvent: data payload

  /// GridNodeEvent: serialization method
  void serialize_order(SST::Core::Serialization::serializer& ser) override{
    Event::serialize_order(ser);
    SST_SER(data)
  }

  /// GridNodeEvent: serialization implementor
  ImplementSerializable(SST::GridNode::GridNodeEvent);

};  // class GridNodeEvent

// -------------------------------------------------------
// GridNode
// -------------------------------------------------------
class GridNode : public SST::Component{
public:
  /// GridNode: top-level SST component constructor
  GridNode( SST::ComponentId_t id, const SST::Params& params );

  /// GridNode: top-level SST component destructor
  ~GridNode();

  /// GridNode: standard SST component 'setup' function
  void setup() override;

  /// GridNode: standard SST component 'finish' function
  void finish() override;

  /// GridNode: standard SST component init function
  void init( unsigned int phase ) override;

  /// GridNode: standard SST component printStatus
  void printStatus(Output& out) override;

  /// GridNode: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // GridNode Component Registration Data
  // -------------------------------------------------------
  /// GridNode: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( GridNode,     // component class
                              "grid",       // component library
                              "GridNode",   // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "GRIDNODE SST COMPONENT",
                              COMPONENT_CATEGORY_UNCATEGORIZED )

  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",         "Sets the verbosity level of output",   "0" },
    {"numBytes",        "Internal state size (4 byte increments)", "64KB"},
    {"numPorts",        "Number of external ports",             "1" },
    {"minData",         "Minimum number of unsigned values",    "1" },
    {"maxData",         "Maximum number of unsigned values",    "2" },
    {"clockDelay",      "Clock delay between sends",            "1" },
    {"clocks",          "Clock cycles to execute",              "1000"},
    {"baseSeed",        "Base seed value",                      "1223"},
    {"rngSeed",         "Mersenne RNG Seed",                    "1223"},
    {"clockFreq",       "Clock frequency",                      "1GHz"},
  )

  // -------------------------------------------------------
  // GridNode Component Port Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_PORTS(
    {"port%(num_ports)d",
      "Ports which connect to endpoints.",
      {"chkpnt.GridNodeEvent", ""}
    }
  )

  // -------------------------------------------------------
  // GridNode SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // GridNode Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS()

  // -------------------------------------------------------
  // GridNode Component Checkpoint Methods
  // -------------------------------------------------------
  /// GridNode: serialization constructor
  GridNode() : SST::Component() {}

  /// GridNode: serialization
  void serialize_order(SST::Core::Serialization::serializer& ser) override;

  /// GridNode: serialization implementations
  ImplementSerializable(SST::GridNode::GridNode)

private:
  // -- internal handlers
  SST::Output    output;                          ///< SST output handler
  TimeConverter* timeConverter;                   ///< SST time conversion handler
  SST::Clock::HandlerBase* clockHandler;          ///< Clock Handler

  // -- parameters
  uint64_t numBytes;                              ///< number of bytes of internal state
  unsigned numPorts;                              ///< number of ports to configure
  uint64_t minData;                               ///< minimum number of data elements
  uint64_t maxData;                               ///< maxmium number of data elements
  uint64_t clockDelay;                            ///< clock delay between sends
  uint64_t clocks;                                ///< number of clocks to execute
  unsigned baseSeed;                              ///< base seed value
  uint64_t curCycle;                              ///< current cycle delay

  // -- internal state
  std::vector<std::string> portname;              ///< port 0 to numPorts names
  std::vector<SST::Link *> linkHandlers;          ///< LinkHandler objects
  std::vector<unsigned> state;                     ///< internal data structure
  std::map< std::string, SST::RNG::Random* > rng; ///< per port mersenne twister objects

  // -- private methods
  /// event handler
  void handleEvent(SST::Event *ev);
  /// sends data to adjacent links
  void sendData();
  /// calculates the port number for the receiver
  unsigned neighbor(unsigned n);

};  // class GridNode
}   // namespace SST::GridNode

#endif  // _SST_GRIDNODE_H_

// EOF