#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# tcldbg-test1.py
#

import os
import sst

cp0 = sst.Component("t0", "tcldbg.TclDbg")
cp0.addParams({
  "verbose" : 5,
  "minData" : 1,
  "maxData" : 100,
  "clockDelay" : 10,
  "clocks" : 100000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz"
})

cp1 = sst.Component("t1", "tcldbg.TclDbg")
cp1.addParams({
  "verbose" : 5,
  "minData" : 1,
  "maxData" : 100,
  "clockDelay" : 10,
  "clocks" : 100000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz"
})

# EOF
