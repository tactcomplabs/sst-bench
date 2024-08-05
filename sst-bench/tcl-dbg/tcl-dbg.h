//
// _tcl-dbg_h_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#ifndef _SST_TCLDBG_H_
#define _SST_TCLDBG_H_

// -- Standard Headers
#include <vector>
#include <queue>
#include <random>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <time.h>
#include <chrono>

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

// -- SST Dbg Headers
#include <sst/dbg/SSTDebug.h>

namespace SST::TclDbg{

// -------------------------------------------------------
// TclDbg
// -------------------------------------------------------
class TclDbg : public SST::Component{
public:
  /// TclDbg: top-level SST component constructor
  TclDbg( SST::ComponentId_t id, const SST::Params& params );

  /// TclDbg: top-level SST component destructor
  ~TclDbg();

  /// TclDbg: standard SST component 'setup' function
  void setup() override;

  /// TclDbg: standard SST component 'finish' function
  void finish() override;

  /// TclDbg: standard SST component init function
  void init( unsigned int phase ) override;

  /// TclDbg: standard SST component printStatus
  void printStatus(Output& out) override;

  /// TclDbg: standard SST component clock function
  bool clockTick( SST::Cycle_t currentCycle );

  // -------------------------------------------------------
  // TclDbg Component Registration Data
  // -------------------------------------------------------
  /// TclDbg: Register the component with the SST core
  SST_ELI_REGISTER_COMPONENT( TclDbg,     // component class
                              "tcldbg",   // component library
                              "TclDbg",   // component name
                              SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
                              "TCLDBG SST COMPONENT",
                              COMPONENT_CATEGORY_UNCATEGORIZED )

  SST_ELI_DOCUMENT_PARAMS(
    {"verbose",         "Sets the verbosity level of output",   "0" },
    {"minData",         "Minimum number of unsigned values",    "1" },
    {"maxData",         "Maximum number of unsigned values",    "2" },
    {"clockDelay",      "Clock delay between sends",            "1" },
    {"clocks",          "Clock cycles to execute",              "1000"},
    {"rngSeed",         "Mersenne RNG Seed",                    "1223"},
    {"clockFreq",       "Clock frequency",                      "1GHz"},
  )

  // -------------------------------------------------------
  // TclDbg Component Port Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_PORTS()

  // -------------------------------------------------------
  // TclDbg SubComponent Parameter Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS()

  // -------------------------------------------------------
  // TclDbg Component Statistics Data
  // -------------------------------------------------------
  SST_ELI_DOCUMENT_STATISTICS(
    {"statBytes", "Number of bytes written",      "bytes",  1},
    {"statTiming","Timing info in microseconds",  "usecs",  1},
  )

  // -------------------------------------------------------
  // TclDbg Component Checkpoint Methods
  // -------------------------------------------------------
  /// TclDbg: serialization constructor
  TclDbg() : SST::Component() {}

  /// TclDbg: serialization
  void serialize_order(SST::Core::Serialization::serializer& ser) override;

  /// TclDbg: serialization implementations
  ImplementSerializable(SST::TclDbg::TclDbg)

private:
  // -- internal handlers
  SST::Output    output;                          ///< SST output handler
  TimeConverter* timeConverter;                   ///< SST time conversion handler
  SST::Clock::HandlerBase* clockHandler;          ///< Clock Handler

  // -- parameters
  unsigned numPorts;                              ///< number of ports to configure
  uint64_t minData;                               ///< minimum number of data elements
  uint64_t maxData;                               ///< maxmium number of data elements
  uint64_t clockDelay;                            ///< clock delay between updates
  uint64_t clocks;                                ///< number of clocks to execute
  uint64_t curCycle;                              ///< current cycle delay

  std::vector<unsigned> data;                     ///< internal data container

  Statistic<uint64_t> *statBytes;                 ///< number of bytes
  Statistic<uint64_t> *statTiming;                ///< timing info

  // -- rng objects
  SST::RNG::Random* mersenne;                     ///< mersenne twister object

  // -- debugging objects
  SSTDebug *Dbg;                                  ///< debugging object

  // -- private methods
  /// TclDbg: update the internal data
  void updateData();

};  // class TclDbg
}   // namespace SST::TclDbg

#endif  // _SST_CHKPNT_H_

// EOF
