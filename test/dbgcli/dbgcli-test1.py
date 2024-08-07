#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# dbgcli-test1.py
#

import os
import sst

DEBUG_PORT = int(os.getenv("DEBUG_PORT", 0))
VERBOSE = 1

cp0 = sst.Component("cp0", "dbgcli.DbgCLI")
cp0.addParams({
  "verbose" : VERBOSE,
  "numPorts" : 1,
  "minData" : 1,
  "maxData" : 100,
  "clockDelay" : 100,
  "clocks" : 10000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz"
})

cp1 = sst.Component("cp1", "dbgcli.DbgCLI")
cp1.addParams({
  "verbose" : VERBOSE,
  "numPorts" : 1,
  "minData" : 1,
  "maxData" : 100,
  "clockDelay" : 100,
  "clocks" : 10000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz",
  "debugPort" : DEBUG_PORT,
})

link0 = sst.Link("link0")
link0.connect( (cp0, "port0", "1us"), (cp1, "port0", "1us") )

# EOF
