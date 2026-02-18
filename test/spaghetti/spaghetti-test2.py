#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# spaghetti-test2.py
#

import os
import sst


s0 = sst.Component("s0", "spaghetti.Spaghetti")
s0.addParams({
  "verbose"      : 9,
  "numPorts"     : 100,
  "numMsgs"      : 100,
  "bytesPerMsg"  : 64,
  "rngSeed"      : 3131
})

s1 = sst.Component("s1", "spaghetti.Spaghetti")
s1.addParams({
  "verbose"      : 9,
  "numPorts"     : 100,
  "numMsgs"      : 100,
  "bytesPerMsg"  : 64,
  "rngSeed"      : 3731
})


for i in range(100):
    linkX = sst.Link("link"+str(i))
    linkX.connect( (s0, "port"+str(i), "1us"),
                   (s1, "port"+str(i), "1us") )

# EOF
