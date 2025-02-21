//
// _restore_h_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_RESTORE_H_
#define _SST_RESTORE_H_

// clang-format off
// -- Standard Headers
#include <vector>
#include <queue>
#include <random>
#include <stdio.h>
#include <stdlib.h>
// #include <inttypes.h>
#include <time.h>

// -- SST Headers
#include "SST.h"
#include <sst/core/rng/distrib.h>
#include <sst/core/rng/rng.h>
#include <sst/core/rng/mersenne.h>
// clang-format on

namespace SST::Restore{

// -------------------------------------------------------
// Restore
// -------------------------------------------------------
class Restore : public SST::Component{
public:
  /// Restore: top-level SST component constructor
  Restore( SST::ComponentId_t id, const SST::Params& params );

  /// Restore: top-level SST component destructor
  ~Restore();

  /// Restore: standard SST component 'setup' function
  void setup() override;

  /// Restore: standard SST component 'finish' function
  void finish() override;

  /// Restore: standard SST component init function
  void init( unsigned int phase ) override;

  /// Restore: standard SST component printStatus
  void printStatus(Output& out) override;

  /// Restore: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // Restore Component Registration Data
  // -------------------------------------------------------
  /// Restore: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( Restore,     // component class
                              "restore",   // component library
                              "Restore",   // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "RESTORE SST COMPONENT",
                              COMPONENT_CATEGORY_UNCATEGORIZED )

  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",         "Sets the verbosity level of output",   "0" },
    {"numBytes",        "Sets the number of stored bytes (4 byte increments)", "64KB"},
    {"clocks",          "Clock cycles to execute",              "1000"},
    {"rngSeed",         "Mersenne RNG Seed",                    "1223"},
    {"clockFreq",       "Clock frequency",                      "1GHz"},
  )

  // -------------------------------------------------------
  // Restore Component Port Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_PORTS()

  // -------------------------------------------------------
  // Restore SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // Restore Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS()

  // -------------------------------------------------------
  // Restore Component Checkpoint Methods
  // -------------------------------------------------------
  /// Restore: serialization constructor
  Restore() : SST::Component() {}

  /// Restore: serialization
  void serialize_order(SST::Core::Serialization::serializer& ser) override;

  /// Restore: serialization implementations
  ImplementSerializable(SST::Restore::Restore)

private:
  // -- internal handlers
  SST::Output    output;                          ///< SST output handler
  TimeConverter* timeConverter;                   ///< SST time conversion handler
  SST::Clock::HandlerBase* clockHandler;          ///< Clock Handler

  // -- parameters
  uint64_t numBytes;                              ///< number of bytes to store
  uint64_t clocks;                                ///< number of clocks to execute

  // -- rng objects
  SST::RNG::Random* mersenne;                     ///< mersenne twister object

  // -- internal data
  std::vector<unsigned> data;                     ///< internal data structure

};  // class Restore
}   // namespace SST::Restore

#endif  // _SST_RESTORE_H_

// EOF
