//
// _micro-comp_h_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_MICROCOMP_H_
#define _SST_MICROCOMP_H_

// -- Standard Headers
#include <vector>
#include <queue>
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

namespace SST::MicroComp{

// -------------------------------------------------------
// MicroComp
// -------------------------------------------------------
class MicroComp : public SST::Component{
public:
  /// MicroComp: top-level SST component constructor
  MicroComp( SST::ComponentId_t id, const SST::Params& params );

  /// MicroComp: top-level SST component destructor
  ~MicroComp();

  /// MicroComp: standard SST component 'setup' function
  void setup();

  /// MicroComp: standard SST component 'finish' function
  void finish();

  /// MicroComp: standard SST component init function
  void init( unsigned int phase );

  /// MicroComp: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // MicroComp Component Registration Data
  // -------------------------------------------------------
  /// MicroComp: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( MicroComp,     // component class
                              "microcomp",   // component library
                              "MicroComp",   // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "MICRO-COMP SST COMPONENT",
                              COMPONENT_CATEGORY_UNCATEGORIZED )

  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",         "Sets the verbosity level of output",   "0" },
  )

  // -------------------------------------------------------
  // MicroComp SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // MicroComp Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS()

private:
  // -- internal handlers
  SST::Output    output;                          ///< SST output handler
  TimeConverter* timeConverter;                   ///< SST time conversion handler
  SST::Clock::Handler<MicroComp>* clockHandler;   ///< Clock Handler

};  // class MicroComp
}   // namespace SST::MicroComp

#endif  // _SST_MICROCOMP_H_

// EOF
