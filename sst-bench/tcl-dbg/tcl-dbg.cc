//
// _tcl-dbg_cc_
//
// Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
// All Rights Reserved
// contact@tactcomplabs.com
//
// See LICENSE in the top level directory for licensing details
//

#include "tcl-dbg.h"

namespace SST::TclDbg{

//------------------------------------------
// TclDbg
//------------------------------------------
TclDbg::TclDbg(SST::ComponentId_t id, const SST::Params& params ) :
  SST::Component( id ), timeConverter(nullptr), clockHandler(nullptr),
  numPorts(1), minData(1), maxData(2), clockDelay(1), clocks(1000),
  curCycle(0) {

  const int Verbosity = params.find< int >( "verbose", 0 );
  output.init(
    "TclDbg[" + getName() + ":@p:@t]: ",
    Verbosity, 0, SST::Output::STDOUT );
  const std::string cpuClock = params.find< std::string >("clockFreq", "1GHz");
  clockHandler  = new SST::Clock::Handler2<TclDbg,&TclDbg::clockTick>(this);
  timeConverter = registerClock(cpuClock, clockHandler);
  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();

  // read the rest of the parameters
  minData = params.find<uint64_t>("minData", 1);
  maxData = params.find<uint64_t>("maxData", 2);
  clockDelay = params.find<uint64_t>("clockDelay", 1);
  clocks = params.find<uint64_t>("clocks", 1000);

  // sanity check the params
  if( maxData < minData ){
    output.fatal(CALL_INFO, -1,
                 "%s : maxData < minData\n",
                 getName().c_str());
  }

  // setup the rng
  mersenne = new SST::RNG::MersenneRNG(params.find<unsigned int>("rngSeed", 1223));

  // setup the debugging object
  Dbg = new SSTDebug(getName(),"./");

  // constructor complete
  output.verbose( CALL_INFO, 5, 0, "Constructor complete\n" );
}

TclDbg::~TclDbg(){
  delete Dbg;
}

void TclDbg::setup(){
}

void TclDbg::finish(){
}

void TclDbg::init( unsigned int phase ){
}

void TclDbg::printStatus( Output& out ){
  out.verbose(CALL_INFO, 1, 0, "DUMPING DATA...\n");
  Dbg->dump(getCurrentSimCycle(),
            DARG((uint64_t)(getCurrentSimCycle())));
  for( unsigned i=0; i<data.size(); i++ ){
    if( !Dbg->dump(getCurrentSimCycle(),
                   DARG(data[i])) ){
      out.output("!!!!!!!!!!!!!!!!!!!!!! DEBUG DUMP FAILED !!!!!!!!!!!!!!!!!!!!!!\n");
    }
  }
}

void TclDbg::serialize_order(SST::Core::Serialization::serializer& ser){
  SST::Component::serialize_order(ser);
  SST_SER(clockHandler)
  SST_SER(numPorts)
  SST_SER(minData)
  SST_SER(maxData)
  SST_SER(clockDelay)
  SST_SER(clocks)
  SST_SER(curCycle)
  SST_SER(data)
  SST_SER(mersenne)
}

void TclDbg::updateData(){
  // generate new data
  data.clear();
  unsigned range = maxData - minData + 1;
  unsigned r = rand() % range + minData;
  for( unsigned i=0; i<r; i++ ){
    data.push_back((unsigned)(mersenne->generateNextUInt32()));
  }
}

bool TclDbg::clockTick( SST::Cycle_t currentCycle ){

  // check to see whether we need to send data over the links
  curCycle++;
  if( curCycle >= clockDelay ){
    updateData();
    curCycle = 0;
  }

  // check to see if we've reached the completion state
  if( (uint64_t)(currentCycle) >= clocks ){
    output.verbose(CALL_INFO, 1, 0,
                   "%s ready to end simulation\n",
                   getName().c_str());
    primaryComponentOKToEndSim();
    return true;
  }

  return false;
}

} // namespace SST::TclDbg

// EOF
