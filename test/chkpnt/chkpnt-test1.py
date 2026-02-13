#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# chkpnt-test1.py
#

import os
import sst

cp0 = sst.Component("cp0", "chkpnt.Chkpnt")
cp0.addParams({
  "verbose" : 5,
  "numPorts" : 1,
  "minData" : 1,
  "maxData" : 100,
  "clockDelay" : 100,
  "clocks" : 10000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz"
})

cp1 = sst.Component("cp1", "chkpnt.Chkpnt")
cp1.addParams({
  "verbose" : 5,
  "numPorts" : 1,
  "minData" : 1,
  "maxData" : 100,
  "clockDelay" : 100,
  "clocks" : 10000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz"
})

link0 = sst.Link("link0")
link0.connect( (cp0, "port0", "1us"), (cp1, "port0", "1us") )

# EOF
