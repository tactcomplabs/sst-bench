//
// _restart_h_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_RESTART_H_
#define _SST_RESTART_H_

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

namespace SST::Restart{

// -------------------------------------------------------
// Restart
// -------------------------------------------------------
class Restart : public SST::Component{
public:
  /// Restart: top-level SST component constructor
  Restart( SST::ComponentId_t id, const SST::Params& params );

  /// Restart: top-level SST component destructor
  ~Restart();

  /// Restart: standard SST component 'setup' function
  void setup() override;

  /// Restart: standard SST component 'finish' function
  void finish() override;

  /// Restart: standard SST component init function
  void init( unsigned int phase ) override;

  /// Restart: standard SST component printStatus
  void printStatus(Output& out) override;

  /// Restart: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // Restart Component Registration Data
  // -------------------------------------------------------
  /// Restart: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( Restart,     // component class
                              "restart",   // component library
                              "Restart",   // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "RESTART SST COMPONENT",
                              COMPONENT_CATEGORY_UNCATEGORIZED )

  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",         "Sets the verbosity level of output",   "0" },
    {"numBytes",        "Sets the number of stored bytes (4 byte increments)", "64KB"},
    {"clocks",          "Clock cycles to execute",              "1000"},
    {"baseSeed",        "Base seed value",                      "1223"},
    {"clockFreq",       "Clock frequency",                      "1GHz"},
  )

  // -------------------------------------------------------
  // Restart Component Port Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_PORTS()

  // -------------------------------------------------------
  // Restart SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // Restart Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS()

  // -------------------------------------------------------
  // Restart Component Checkpoint Methods
  // -------------------------------------------------------
  /// Restart: serialization constructor
  Restart() : SST::Component() {}

  /// Restart: serialization
  void serialize_order(SST::Core::Serialization::serializer& ser) override;

  /// Restart: serialization implementations
  ImplementSerializable(SST::Restart::Restart)

private:
  // -- internal handlers
  SST::Output    output;                          ///< SST output handler
  TimeConverter* timeConverter;                   ///< SST time conversion handler
  SST::Clock::HandlerBase* clockHandler;          ///< Clock Handler

  // -- parameters
  uint64_t numBytes;                              ///< number of bytes to store
  uint64_t clocks;                                ///< number of clocks to execute
  unsigned baseSeed;                              ///< base seed value

  // -- internal data
  std::vector<unsigned> data;                     ///< internal data structure

};  // class Restart
}   // namespace SST::Restart

#endif  // _SST_RESTART_H_

// EOF
