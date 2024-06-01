//
// _chkpnt_h_
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

namespace SST::Chkpnt{

// -------------------------------------------------------
// ChkpntEvent
// -------------------------------------------------------
class ChkpntEvent : public SST::Event{
public:
  /// ChkpntEvent : standard constructor
  ChkpntEvent() : SST::Event() {}

  /// ChkpntEvent: constructor
  ChkpntEvent(std::vector<unsigned> d) : SST::Event(), data(d) {}
  ~ChkpntEvent();

  /// ChkpntEvent: retrieve the data
  std::vector<unsigned> getData() { return data; }

private:
  std::vector<unsigned> data;     ///< ChkpntEvent: data payload

  /// ChkpntEvent: serialization method
  void serialize_order(SST::Core::Serialization::serializer& ser) override{
    Event::serialize_order(ser);
    SST_SER(data);
  }

  /// ChkpntEvent: serialization implementor
  ImplementSerializable(SST::Chkpnt::ChkpntEvent);

};  // class ChkpntEvent

// -------------------------------------------------------
// Chkpnt
// -------------------------------------------------------
class Chkpnt : public SST::Component{
public:
  /// Chkpnt: top-level SST component constructor
  Chkpnt( SST::ComponentId_t id, const SST::Params& params );

  /// Chkpnt: top-level SST component destructor
  ~Chkpnt();

  /// Chkpnt: standard SST component 'setup' function
  void setup();

  /// Chkpnt: standard SST component 'finish' function
  void finish();

  /// Chkpnt: standard SST component init function
  void init( unsigned int phase );

  /// Chkpnt: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // Chkpnt Component Registration Data
  // -------------------------------------------------------
  /// Chkpnt: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( Chkpnt,     // component class
                              "chkpnt",   // component library
                              "Chkpnt",   // component name
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
    {"clockFreq",       "Clock frequency",                      "1GHz"},
  )

  // -------------------------------------------------------
  // Chkpnt Component Port Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_PORTS(
    {"port%(num_ports)d",
      "Ports which connect to endpoints.",
      {"chkpnt.ChkpntEvent", ""}
    }
  )

  // -------------------------------------------------------
  // Chkpnt SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // Chkpnt Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS()

  // -------------------------------------------------------
  // Chkpnt Component Checkpoint Methods
  // -------------------------------------------------------
  /// Chkpnt: serialization constructor
  Chkpnt() : SST::Component() {}

  /// Chkpnt: serialization
  void serialize_order(SST::Core::Serialization::serializer& ser) override;

  /// Chkpnt: serialization implementations
  ImplementSerializable(SST::Chkpnt::Chkpnt)

private:
  // -- internal handlers
  SST::Output    output;                          ///< SST output handler
  TimeConverter* timeConverter;                   ///< SST time conversion handler
  SST::Clock::HandlerBase* clockHandler;          ///< Clock Handler

  std::vector<SST::Link *> linkHandlers;          ///< LinkHandler objects

};  // class Chkpnt
}   // namespace SST::Chkpnt

#endif  // _SST_MICROCOMP_H_

// EOF
