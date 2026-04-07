//
// _large-stat-chkpnt_h_
//
// Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_LARGESTATCHKPNT_H_
#define _SST_LARGESTATCHKPNT_H_

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

namespace SST::LargeStatChkpnt{

// -------------------------------------------------------
// LargeStatChkpnt
// -------------------------------------------------------
class LargeStatChkpnt : public SST::Component{
public:
  /// LargeStat: top-level SST component constructor
  LargeStatChkpnt( SST::ComponentId_t id, const SST::Params& params );

  /// LargeStatChkpnt: top-level SST component destructor
  ~LargeStatChkpnt();

  /// LargeStatChkpnt: standard SST component 'setup' function
  void setup() override;

  /// LargeStatChkpnt: standard SST component 'finish' function
  void finish() override;

  /// LargeStatChkpnt: standard SST component init function
  void init( unsigned int phase ) override;

  /// LargeStatChkpnt: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // LargeStatChkpnt Component Registration Data
  // -------------------------------------------------------
  /// LargeStatChkpnt: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( LargeStatChkpnt,     // component class
                              "largestatchkpnt",   // component library
                              "LargeStatChkpnt",   // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "LARGE-STAT-CHKPNT SST COMPONENT",
                              COMPONENT_CATEGORY_UNCATEGORIZED )

  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",         "Sets the verbosity level of output",           "0" },
    {"numStats",        "Sets the number of stats to create",           "1" },
    {"numClocks",       "Sets the number of clock cycles to execute",   "1" },
  )

  // -------------------------------------------------------
  // LargeStatChkpnt SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // LargeStatChkpnt Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS(
    {"STAT_", "Basic stat handler", "count", 1},
  )

  // -------------------------------------------------------
  // LargeStatChkpnt Component Checkpoint Methods
  // -------------------------------------------------------
  /// Chkpnt: serialization constructor
  LargeStatChkpnt() : SST::Component() {}

  /// LargeStatChkpnt: serialization
  void serialize_order(SST::Core::Serialization::serializer& ser) override;

  /// LargeStatChkpnt: serialization implementations
  ImplementSerializable(SST::LargeStatChkpnt::LargeStatChkpnt)

private:
  // -- internal handlers
  SST::Output    output;                          ///< SST output handler
  TimeConverter* timeConverter;                   ///< SST time conversion handler
  SST::Clock::HandlerBase* clockHandler;          ///< Clock Handler

  uint64_t numStats;                              ///< Number of stats to create
  uint64_t numClocks;                             ///< Number of clock cycles to run

  std::vector<Statistic<uint64_t>*> VStat;        ///< Statistics vector

};  // class LargeStatChkpnt
}   // namespace SST::LargeStatChkpnt

#endif  // _SST_LARGESTATCHKPNT_H_

// EOF
