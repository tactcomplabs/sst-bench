#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# noodle-test2.py
#

import os
import sst


n0 = sst.Component("n0", "noodle.Noodle")
n0.addParams({
  "verbose"      : 9,
  "clockFreq"    : "1GHz",
  "numPorts"     : 8,
  "msgPerClock"  : 3,
  "bytesPerClock": 4,
  "portsPerClock": 3,
  "clocks"       : 100000,
  "rngSeed"      : 3131
})

n1 = sst.Component("n1", "noodle.Noodle")
n1.addParams({
  "verbose"      : 9,
  "clockFreq"    : "1GHz",
  "numPorts"     : 8,
  "msgPerClock"  : 9,
  "bytesPerClock": 7,
  "portsPerClock": 5,
  "clocks"       : 100000,
  "rngSeed"      : 3131
})

link0 = sst.Link("link0")
link1 = sst.Link("link1")
link2 = sst.Link("link2")
link3 = sst.Link("link3")
link4 = sst.Link("link4")
link5 = sst.Link("link5")
link6 = sst.Link("link6")
link7 = sst.Link("link7")
link0.connect( (n0, "port0", "1us"), (n1, "port0", "1us") )
link1.connect( (n0, "port1", "1us"), (n1, "port1", "1us") )
link2.connect( (n0, "port2", "1us"), (n1, "port2", "1us") )
link3.connect( (n0, "port3", "1us"), (n1, "port3", "1us") )
link4.connect( (n0, "port4", "1us"), (n1, "port4", "1us") )
link5.connect( (n0, "port5", "1us"), (n1, "port5", "1us") )
link6.connect( (n0, "port6", "1us"), (n1, "port6", "1us") )
link7.connect( (n0, "port7", "1us"), (n1, "port7", "1us") )

# EOF
