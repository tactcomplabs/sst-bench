//
// _gridnode_h_
//
// Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
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
#include <time.h>
#include <iomanip>

// clang-format off
// -- SST Headers
#include "SST.h"
#include <sst/core/rng/distrib.h>
#include <sst/core/rng/rng.h>
#include <sst/core/rng/mersenne.h>
// clang-format on

// Static TUT selection
#define TUT uint32_t
// #define TUT StructUint8x4
// #define TUT VecUint8x4
// #define TUT Tuple8x4
// #define TUT PairPair

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
    SST_SER(data);
  }

  /// GridNodeEvent: serialization implementor
  ImplementSerializable(SST::GridNode::GridNodeEvent);

};  // class GridNodeEvent

// -------------------------------------------------------
// GridState
// -------------------------------------------------------
template <typename T>
class GridState : public SST::Core::Serialization::serializable {
private:
  std::vector<T> state;
public:
  GridState(std::vector<T> data) : state(data) {}
  void push_back(T d) { state.push_back(d); }
  size_t size() { return state.size(); }
  class Iterator {
    private:
      typename std::vector<T>::iterator it;
    public:
      Iterator(typename std::vector<T>::iterator it) : it(it) {}
      T& operator*() { return *it;}
      Iterator& operator++() { ++it; return *this;}
      bool operator!=(const Iterator& other) const { return it != other.it; }
  }; // class Iterator
  Iterator begin() { return Iterator(state.begin()); }
  Iterator end() { return Iterator(state.end()); }
  // serialization
  GridState() {};
  void serialize_order(SST::Core::Serialization::serializer& ser) override {
    SST_SER(state);
  }
  // This has public and private sections. Put last!                                                                                                         
  ImplementSerializable(SST::GridNode::GridState<T>);
}; // class GridState

// ----------------------------------------------------------
// StructUint8x4: Same size as uint32_t but using 4 elements
// ----------------------------------------------------------
struct StructUint8x4 final : public SST::Core::Serialization::serializable {
  uint8_t a;
  uint8_t b;
  uint8_t c;
  uint8_t d;
  StructUint8x4(uint64_t n) {
    a = uint8_t(n);
    b = uint8_t(n);
    c = uint8_t(n);
    d = uint8_t(n);
  }
  // operator overloading
  StructUint8x4 operator++(int) {
    StructUint8x4 old = *this;
    a++; b++; c++; d++;
    return old;
  }
  StructUint8x4 operator+=(const StructUint8x4& rhs) {
    a += rhs.a;
    b += rhs.b;
    c += rhs.c;
    d += rhs.d;
    return *this;
  }
  friend StructUint8x4 operator+(StructUint8x4 lhs, const uint32_t& rhs) {
    lhs.a += uint8_t(rhs);
    lhs.b += uint8_t(rhs);
    lhs.c += uint8_t(rhs);
    lhs.d += uint8_t(rhs);
    return lhs;
  }
  inline bool operator==(const StructUint8x4& rhs) {
    bool ea = (a==rhs.a);
    bool eb = (b==rhs.b);
    bool ec = (c==rhs.c);
    bool ed = (d==rhs.d);
    return ea && eb && ec && ed;
  }
  inline bool operator!=(const StructUint8x4& rhs) {
    return !(*this == rhs);
  }
  // special scalar compare
  inline bool operator==(const uint32_t& rhs) {
    uint8_t e = uint8_t(rhs);
    bool ea = (a==e);
    bool eb = (b==e);
    bool ec = (c==e);
    bool ed = (d==e);
    return ea && eb && ec && ed;
  }
  inline bool operator!=(const uint32_t& rhs) {
    return !(*this == rhs);
  }

  // serialization
  StructUint8x4() {};
  void serialize_order(SST::Core::Serialization::serializer& ser) override {
    SST_SER(a);
    SST_SER(b);
    SST_SER(c);
    SST_SER(d);
  };
  // This has public and private sections. Put last!
  ImplementSerializable(SST::GridNode::StructUint8x4) ;
}; // struct StructUint8x4

// StructUint8x4 ostream overload
std::ostream& operator<<(std::ostream& os, const StructUint8x4& obj) {
  os << std::hex << std::setfill('0') << std::setw(2) << "{ 0x*" << (uint16_t)obj.a << ",0x*" << (uint16_t)obj.b << ",0x*" << (uint16_t)obj.c << ",0x*" << (uint16_t)obj.d << "}";
  return os;
}

#ifdef VecUint8x4
// -------------------------------------------------------------
// VecUint8x4: Same size as uint32_t but using 4 vector elements
// -------------------------------------------------------------
struct VecUint8x4 final : public SST::Core::Serialization::serializable {
  std::vector<uint8_t> vec4 = {0,0,0,0};
  VecUint8x4(uint64_t n) {
    vec4.resize(4);
    for (size_t i=0;i<4;i++)
      vec4[i] = uint8_t(n);
  }
  // operator overloading
  VecUint8x4 operator++(int) {
    VecUint8x4 old = *this;
    for (size_t i=0;i<4;i++)
      vec4[i]++;
    return old;
  }
  VecUint8x4 operator+=(const VecUint8x4& rhs) {
    for (size_t i=0;i<4;i++)
      vec4[i] += rhs.vec4[i];
    return *this;
  }
  friend VecUint8x4 operator+(VecUint8x4 lhs, const uint32_t& rhs) {
    for (size_t i=0;i<4;i++)
      lhs.vec4[i] += uint8_t(rhs);
    return lhs;
  }
  inline bool operator==(const VecUint8x4& rhs) {
    bool res = true;
    for (size_t i=0;i<4;i++)
      res &= (vec4[i]==rhs.vec4[i]);
    return res;
  }
  inline bool operator!=(const VecUint8x4& rhs) {
    return !(*this == rhs);
  }
  // special scalar compare
  inline bool operator==(const uint32_t& rhs) {
    bool res = true;
    uint8_t e = uint8_t(rhs);
    for (size_t i=0;i<4;i++)
      res &= (vec4[i]==e);
    return res;
  }
  inline bool operator!=(const uint32_t& rhs) {
    return !(*this == rhs);
  }

  // serialization
  VecUint8x4() {};
  void serialize_order(SST::Core::Serialization::serializer& ser) override {
    SST_SER(vec4);
  };
  // This has public and private sections. Put last!
  ImplementSerializable(SST::GridNode::VecUint8x4) ;
}; // struct VecUint8x4

// VecUint8x4 ostream overload
std::ostream& operator<<(std::ostream& os, const VecUint8x4& obj) {
  os << std::hex << std::setfill('0') << std::setw(2) << "{ 0x*" << (uint16_t)obj.vec4[0] << ",0x*" << (uint16_t)obj.vec4[1] << ",0x*" << (uint16_t)obj.vec4[2] << ",0x*" << (uint16_t)obj.vec4[3] << "}";
  return os;
}
#endif

#ifdef Tuple8x4
// -------------------------------------------------------------
// TupleUint8x4: Same size as uint32_t but using 4 element tuple
// -------------------------------------------------------------
struct Tuple8x4 final : public SST::Core::Serialization::serializable {
  std::tuple<uint8_t, uint8_t, uint8_t, uint8_t> tup4 = {0,0,0,0};
  Tuple8x4(uint64_t n) {
    tup4 = { n,n,n,n };
  }
  // operator overloading
  Tuple8x4 operator++(int) {
    Tuple8x4 old = *this;
    for (size_t i=0;i<4;i++)
      tup4 = { std::get<0>(tup4) + 1, std::get<1>(tup4) + 1, std::get<2>(tup4) + 1, std::get<3>(tup4) + 1 };
    return old;
  }
  Tuple8x4 operator+=(const Tuple8x4& rhs) {
    tup4 = { 
      std::get<0>(tup4) + std::get<0>(rhs.tup4),
      std::get<1>(tup4) + std::get<1>(rhs.tup4),
      std::get<2>(tup4) + std::get<2>(rhs.tup4),
      std::get<3>(tup4) + std::get<3>(rhs.tup4),
    };
    return *this;
  }
  friend Tuple8x4 operator+(Tuple8x4 lhs, const uint32_t& rhs) {
    lhs.tup4 = { 
      std::get<0>(lhs.tup4) + uint8_t(rhs),
      std::get<1>(lhs.tup4) + uint8_t(rhs),
      std::get<2>(lhs.tup4) + uint8_t(rhs),
      std::get<3>(lhs.tup4) + uint8_t(rhs),
    }; 
    return lhs;
  }
  inline bool operator==(const Tuple8x4& rhs) {
    bool res = true;
    res &= std::get<0>(tup4)==std::get<0>(rhs.tup4);
    res &= std::get<1>(tup4)==std::get<1>(rhs.tup4);
    res &= std::get<2>(tup4)==std::get<2>(rhs.tup4);
    res &= std::get<3>(tup4)==std::get<3>(rhs.tup4);
    return res;
  }
  inline bool operator!=(const Tuple8x4& rhs) {
    return !(*this == rhs);
  }
  // special scalar compare
  inline bool operator==(const uint32_t& rhs) {
    bool res = true;
    uint8_t e = uint8_t(rhs);
    res &= std::get<0>(tup4)==e;
    res &= std::get<1>(tup4)==e;
    res &= std::get<2>(tup4)==e;
    res &= std::get<3>(tup4)==e;
    return res;
  }
  inline bool operator!=(const uint32_t& rhs) {
    return !(*this == rhs);
  }

  // serialization
  Tuple8x4() {};
  void serialize_order(SST::Core::Serialization::serializer& ser) override {
    SST_SER(tup4);
  };
  // This has public and private sections. Put last!
  ImplementSerializable(SST::GridNode::Tuple8x4) ;
}; // struct Tuple8x4

// Tuple8x4 ostream overload
std::ostream& operator<<(std::ostream& os, const Tuple8x4& obj) {
  os << std::hex << std::setfill('0') << std::setw(2) << "{ 0x*" << uint16_t{std::get<0>(obj.tup4)} << ",0x*" << uint16_t {std::get<1>(obj.tup4)} << ",0x*" << uint16_t {std::get<2>(obj.tup4)} << ",0x*" << uint16_t {std::get<3>(obj.tup4)} << "}";
  return os;
}
#endif //Tuple8x4

#ifdef PairPair
// -------------------------------------------------------------
// PairPair: Same size as uint32_t but using a pair of pairs
// -------------------------------------------------------------
struct PairPair final : public SST::Core::Serialization::serializable {
  std::pair<std::pair<uint8_t, uint8_t>,std::pair<uint8_t, uint8_t>> pairpair = { {0,0}, {0,0} };
  PairPair(uint64_t n) {
    pairpair = { {n,n}, {n,n} };
  }
  // operator overloading
  PairPair operator++(int) {
    PairPair old = *this;
    pairpair.first = { pairpair.first.first++, pairpair.first.second++ };
    pairpair.second = { pairpair.second.first++, pairpair.second.second++ };
    return old;
  }
  PairPair operator+=(const PairPair& rhs) {
    pairpair.first.first   += rhs.pairpair.first.first;
    pairpair.first.second  += rhs.pairpair.first.second;
    pairpair.second.first  += rhs.pairpair.second.first;
    pairpair.second.second += rhs.pairpair.second.second;
    return *this;
  }
  friend PairPair operator+(PairPair lhs, const uint32_t& rhs) {
    uint8_t v = uint8_t(rhs);
    lhs.pairpair.first.first = lhs.pairpair.first.first + v;
    lhs.pairpair.first.second = lhs.pairpair.first.second + v;
    lhs.pairpair.second.first = lhs.pairpair.second.first + v;
    lhs.pairpair.second.second = lhs.pairpair.second.second + v;
    return lhs;
  }
  inline bool operator==(const PairPair& rhs) {
    bool res = true;
    res &= pairpair.first.first == rhs.pairpair.first.first;
    res &= pairpair.first.second == rhs.pairpair.first.second;
    res &= pairpair.second.first == rhs.pairpair.second.first;
    res &= pairpair.second.second == rhs.pairpair.second.second;
    return res;
  }
  inline bool operator!=(const PairPair& rhs) {
    return !(*this == rhs);
  }
  // special scalar compare
  inline bool operator==(const uint32_t& rhs) {
    bool res = true;
    uint8_t e = uint8_t(rhs);
    res &= pairpair.first.first == e;
    res &= pairpair.first.second == e;
    res &= pairpair.second.first == e;
    res &= pairpair.second.second == e;
    return res;
  }
  inline bool operator!=(const uint32_t& rhs) {
    return !(*this == rhs);
  }

  // serialization
  PairPair() {};
  void serialize_order(SST::Core::Serialization::serializer& ser) override {
    SST_SER(pairpair);
  };
  // This has public and private sections. Put last!
  ImplementSerializable(SST::GridNode::PairPair) ;
}; // struct PairPair

// PairPair ostream overload
std::ostream& operator<<(std::ostream& os, const PairPair& obj) {
  os << std::hex << std::setfill('0') << std::setw(2) << "{ 0x*" << uint16_t{obj.pairpair.first.first} << ",0x*" << uint16_t {obj.pairpair.first.second} << ",0x*" << uint16_t {obj.pairpair.second.first} << ",0x*" << uint16_t {obj.pairpair.second.second} << "}";
  return os;
}
#endif //PairPair

// -------------------------------------------------------
// GridNode
// -------------------------------------------------------
class GridNode final : public SST::Component{
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
    {"numBytes",        "Internal state size (4 byte increments)", "16384"},
    {"numPorts",        "Number of external ports",             "8" },
    {"minData",         "Minimum number of unsigned values over link",    "10" },
    {"maxData",         "Maximum number of unsigned values over link",    "8192" },
    {"minDelay",        "Minumum clock delay between sends",    "50" },
    {"maxDelay",        "Maximum clock delay between sends",    "100" },
    {"clocks",          "Clock cycles to execute",              "1000"},
    {"clockFreq",       "Clock frequency",                      "1GHz"},
    {"rngSeed",         "Mersenne RNG Seed",                    "1223"},
    {"demoBug",         "Induce bug for debug demo",               "0"},

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
  uint64_t minDelay;                              ///< minimum clock delay between sends
  uint64_t maxDelay;                              ///< maximum clock delay between sends
  uint64_t clocks;                                ///< number of clocks to execute
  unsigned rngSeed;                               ///< base seed for random number generator
  uint64_t curCycle;                              ///< current cycle delay

  // Bug injection
  unsigned demoBug;                               ///< induce bug for debug demonstration
  uint64_t dataMask;                              ///< send only 16 bits of data
  uint64_t dataMax;                               ///< change to inject illegal values

  // -- internal state
  uint64_t clkDelay = 0;                          ///< current clock delay
  std::vector<std::string> portname;              ///< port 0 to numPorts names
  std::vector<SST::Link *> linkHandlers;          ///< LinkHandler objects
  GridState<TUT> state;                           ///< internal data structure
  std::map< std::string, SST::RNG::Random* > rng; ///< per port mersenne twister objects
  SST::RNG::Random* localRNG = 0;                 ///< component local random number generator

  // -- checkpoint debug
  uint64_t cptBegin;
  uint64_t cptEnd;
  uint64_t stateBegin;
  uint64_t stateEnd;

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
