#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# spaghetti-test1.py
#

import os
import sst


s0 = sst.Component("s0", "spaghetti.Spaghetti")
s0.addParams({
  "verbose"      : 9,
  "numPorts"     : 2,
  "numMsgs"      : 100,
  "bytesPerMsg"  : 64,
  "rngSeed"      : 3131
})

s1 = sst.Component("s1", "spaghetti.Spaghetti")
s1.addParams({
  "verbose"      : 9,
  "numPorts"     : 2,
  "numMsgs"      : 100,
  "bytesPerMsg"  : 64,
  "rngSeed"      : 3731
})

link0 = sst.Link("link0")
link0.connect( (s0, "port0", "1us"), (s1, "port0", "1us") )

link1 = sst.Link("link1")
link1.connect( (s0, "port1", "1us"), (s1, "port1", "1us") )

# EOF
