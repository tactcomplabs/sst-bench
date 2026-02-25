#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# flood-test1.py
#

import os
import sst

hub = sst.Component("hub", "flood.Flood")
hub.addParams({
  "verbose"         : 9,
  "clockFreq"       : "1GHz",
  "numPorts"        : 4,
  "gigabytePerMsg"  : 1,
  "portsPerClock"   : 1,
  "msgsPerClock"    : 1,
  "clocks"          : 10,
  "rngSeed"         : 3131,
  "hubComp"         : 1
})


n0 = sst.Component("n0", "flood.Flood")
n0.addParams({
  "verbose"         : 9,
  "clockFreq"       : "1GHz",
  "numPorts"        : 1,
  "gigabytePerMsg"  : 1,
  "portsPerClock"   : 1,
  "clocks"          : 10,
  "rngSeed"         : 3131,
  "hubComp"         : 0
})

n1 = sst.Component("n1", "flood.Flood")
n1.addParams({
  "verbose"         : 9,
  "clockFreq"       : "1GHz",
  "numPorts"        : 1,
  "gigabytePerMsg"  : 1,
  "portsPerClock"   : 1,
  "clocks"          : 10,
  "rngSeed"         : 3131,
  "hubComp"         : 0
})

n2 = sst.Component("n2", "flood.Flood")
n2.addParams({
  "verbose"         : 9,
  "clockFreq"       : "1GHz",
  "numPorts"        : 1,
  "gigabytePerMsg"  : 1,
  "portsPerClock"   : 1,
  "clocks"          : 10,
  "rngSeed"         : 3131,
  "hubComp"         : 0
})

n3 = sst.Component("n3", "flood.Flood")
n3.addParams({
  "verbose"         : 9,
  "clockFreq"       : "1GHz",
  "numPorts"        : 1,
  "gigabytePerMsg"  : 1,
  "portsPerClock"   : 1,
  "clocks"          : 10,
  "rngSeed"         : 3131,
  "hubComp"         : 0
})


link0 = sst.Link("link0")
link0.connect( (hub, "port0", "1us"), (n0, "port0", "1us") )
link1 = sst.Link("link1")
link1.connect( (hub, "port1", "1us"), (n1, "port0", "1us") )
link2 = sst.Link("link2")
link2.connect( (hub, "port2", "1us"), (n2, "port0", "1us") )
link3 = sst.Link("link3")
link3.connect( (hub, "port3", "1us"), (n3, "port0", "1us") )

