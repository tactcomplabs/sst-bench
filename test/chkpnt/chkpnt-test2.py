#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
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
  "verbose" : 0,
  "numPorts" : 10,
  "minData" : 1,
  "maxData" : 10000,
  "clockDelay" : 100,
  "clocks" : 10000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz"
})

cp1 = sst.Component("cp1", "chkpnt.Chkpnt")
cp1.addParams({
  "verbose" : 0,
  "numPorts" : 10,
  "minData" : 1,
  "maxData" : 10000,
  "clockDelay" : 100,
  "clocks" : 10000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz"
})

link0 = sst.Link("link0")
link0.connect( (cp0, "port0", "1us"), (cp1, "port0", "1us") )
link1 = sst.Link("link1")
link1.connect( (cp0, "port1", "1us"), (cp1, "port1", "1us") )
link2 = sst.Link("link2")
link2.connect( (cp0, "port2", "1us"), (cp1, "port2", "1us") )
link3 = sst.Link("link3")
link3.connect( (cp0, "port3", "1us"), (cp1, "port3", "1us") )
link4 = sst.Link("link4")
link4.connect( (cp0, "port4", "1us"), (cp1, "port4", "1us") )
link5 = sst.Link("link5")
link5.connect( (cp0, "port5", "1us"), (cp1, "port5", "1us") )
link6 = sst.Link("link6")
link6.connect( (cp0, "port6", "1us"), (cp1, "port6", "1us") )
link7 = sst.Link("link7")
link7.connect( (cp0, "port7", "1us"), (cp1, "port7", "1us") )
link8 = sst.Link("link8")
link8.connect( (cp0, "port8", "1us"), (cp1, "port8", "1us") )
link9 = sst.Link("link9")
link9.connect( (cp0, "port9", "1us"), (cp1, "port9", "1us") )

# EOF
