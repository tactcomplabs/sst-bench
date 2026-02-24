#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# noodle-test1.py
#

import os
import sst


n0 = sst.Component("n0", "noodle.Noodle")
n0.addParams({
  "verbose"         : 9,
  "randClockRange"  : "1-3",
  "numPorts"        : 1,
  "msgPerClock"     : 1,
  "bytesPerClock"   : 1,
  "portsPerClock"   : 1,
  "clocks"          : 100000,
  "rngSeed"         : 3131
})

n1 = sst.Component("n1", "noodle.Noodle")
n1.addParams({
  "verbose"         : 9,
  "randClockRange"  : "5-9",
  "numPorts"        : 1,
  "msgPerClock"     : 1,
  "bytesPerClock"   : 1,
  "portsPerClock"   : 1,
  "clocks"          : 100000,
  "rngSeed"         : 3131
})

link0 = sst.Link("link0")
link0.connect( (n0, "port0", "1us"), (n1, "port0", "1us") )

# EOF
