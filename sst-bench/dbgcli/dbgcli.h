//
// _dbgcli_h_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_CHKPNT_H_
#define _SST_CHKPNT_H_

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
#include <sst/core/probe.h>
#include <sst/core/statapi/stataccumulator.h>
#include <sst/core/subcomponent.h>
#include <sst/core/timeConverter.h>
#include <sst/core/model/element_python.h>
#include <sst/core/rng/distrib.h>
#include <sst/core/rng/rng.h>
#include <sst/core/rng/mersenne.h>

namespace SST::DbgCLI{

// -------------------------------------------------------
// Debug Control State 
// -------------------------------------------------------
class DbgCLIProbeControl : public SST::ProbeControl {
public:
  DbgCLIProbeControl(SST::Output * out, int probeMode, int probeStartCycle, int probeBufferSize, int probePort);
};

// -------------------------------------------------------
// DbgCLIEvent
// -------------------------------------------------------
class DbgCLIEvent : public SST::Event{
public:
  /// DbgCLIEvent : standard constructor
  DbgCLIEvent() : SST::Event() {}

  /// DbgCLIEvent: constructor
  DbgCLIEvent(std::vector<unsigned> d) : SST::Event(), data(d) {}

  /// DbgCLIEvent: destructor
  ~DbgCLIEvent() {}

  /// DbgCLIEvent: retrieve the data
  std::vector<unsigned> const getData() { return data; }

private:
  std::vector<unsigned> data;     ///< DbgCLIEvent: data payload

  /// DbgCLIEvent: serialization method
  void serialize_order(SST::Core::Serialization::serializer& ser) override{
    Event::serialize_order(ser);
    SST_SER(data)
  }

  /// DbgCLIEvent: serialization implementor
  ImplementSerializable(SST::DbgCLI::DbgCLIEvent);

};  // class DbgCLIEvent

// -------------------------------------------------------
// DbgCLI
// -------------------------------------------------------
class DbgCLI : public SST::Component{
public:
  /// DbgCLI: top-level SST component constructor
  DbgCLI( SST::ComponentId_t id, const SST::Params& params );

  /// DbgCLI: top-level SST component destructor
  ~DbgCLI();

  /// DbgCLI: standard SST component 'setup' function
  void setup() override;

  /// DbgCLI: standard SST component 'finish' function
  void finish() override;

  /// DbgCLI: standard SST component init function
  void init( unsigned int phase ) override;

  /// DbgCLI: standard SST component printStatus
  void printStatus(Output& out) override;

  /// DbgCLI: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  const int DEFAULT_PROBE_BUFFER_SIZE = 1024;

  // -------------------------------------------------------
  // DbgCLI Component Registration Data
  // -------------------------------------------------------
  /// DbgCLI: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( DbgCLI,     // component class
                              "dbgcli",   // component library
                              "DbgCLI",   // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "CHKPNT SST COMPONENT",
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
    {"probeMode",       "0-Disabled,1-Checkpoint based, >1-rsv",  "0"},
    {"probeStartTime", "Use with checkpoint-sim-period",         "0"},
    {"probeBufferSize", "Records in circular trace buffer",    "1024"}, // DEFAULT_PROBE_BUFFER_SIZE
    {"probePort",       "Socket assignment for debug port",      "0" }
  )

  // -------------------------------------------------------
  // DbgCLI Component Port Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_PORTS(
    {"port%(num_ports)d",
      "Ports which connect to endpoints.",
      {"dbgcli.DbgCLIEvent", ""}
    }
  )

  // -------------------------------------------------------
  // DbgCLI SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // DbgCLI Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS()

  // -------------------------------------------------------
  // DbgCLI Component Checkpoint Methods
  // -------------------------------------------------------
  /// DbgCLI: serialization constructor
  DbgCLI() : SST::Component() {}

  /// DbgCLI: serialization
  void serialize_order(SST::Core::Serialization::serializer& ser) override;

  /// DbgCLI: Update debug control state object on checkpoint
  void handle_chkpt_probe_action() override;
  
  /// DbgCLI: serialization implementations
  ImplementSerializable(SST::DbgCLI::DbgCLI)

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

  // -- Component probe state object
 std::unique_ptr<DbgCLIProbeControl> probeControl_;

  // -- rng objects
  SST::RNG::Random* mersenne;                     ///< mersenne twister object

  std::vector<SST::Link *> linkHandlers;          ///< LinkHandler objects

  // -- private methods
  /// event handler
  void handleEvent(SST::Event *ev);

  /// sends data to adjacent links
  void sendData();

};  // class DbgCLI

}   // namespace SST::DbgCLI

#endif  // _SST_CHKPNT_H_

// EOF
