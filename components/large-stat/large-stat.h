//
// _large-stat_h_
//
// Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_LARGESTAT_H_
#define _SST_LARGESTAT_H_

// clang-format off
// -- Standard Headers
#include <vector>
#include <queue>
#include <stdio.h>
#include <stdlib.h>
// #include <inttypes.h>
#include <time.h>

// -- SST Headers
#include "SST.h"
// clang-format on

namespace SST::LargeStat{

// -------------------------------------------------------
// TODO
// -------------------------------------------------------
// When the SST 14+ checkpoint save/restore supports
// statistics, we need to update this microbenchmark
// to checkpoint all the stats.
// - add checkpoint/restore support
// - modify the clock function to support longer runtimes
// -------------------------------------------------------

// -------------------------------------------------------
// LargeStat
// -------------------------------------------------------
class LargeStat : public SST::Component{
public:
  /// LargeStat: top-level SST component constructor
  LargeStat( SST::ComponentId_t id, const SST::Params& params );

  /// LargeStat: top-level SST component destructor
  ~LargeStat();

  /// LargeStat: standard SST component 'setup' function
  void setup() override;

  /// LargeStat: standard SST component 'finish' function
  void finish() override;

  /// LargeStat: standard SST component init function
  void init( unsigned int phase ) override;

  /// LargeStat: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // LargeStat Component Registration Data
  // -------------------------------------------------------
  /// LargeStat: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( LargeStat,     // component class
                              "largestat",   // component library
                              "LargeStat",   // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "LARGE-STAT SST COMPONENT",
                              COMPONENT_CATEGORY_UNCATEGORIZED )

  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",         "Sets the verbosity level of output",   "0" },
    {"numStats",        "Sets the number of stats to create",   "1" },
  )

  // -------------------------------------------------------
  // LargeStat SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // LargeStat Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS(
    {"STAT_", "Basic stat handler", "count", 1},
  )

private:
  // -- internal handlers
  SST::Output    output;                          ///< SST output handler
  TimeConverter* timeConverter;                   ///< SST time conversion handler
  SST::Clock::Handler<LargeStat>* clockHandler;   ///< Clock Handler

  uint64_t numStats;                              ///< Number of stats to create

  std::vector<Statistic<uint64_t>*> VStat;        ///< Statistics vector

};  // class LargeStat
}   // namespace SST::LargeStat

#endif  // _SST_LARGESTAT_H_

// EOF
