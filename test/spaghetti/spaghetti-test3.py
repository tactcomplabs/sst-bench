#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# spaghetti-test3.py
#

import os
import sst

sst.setStatisticLoadLevel(7)
sst.setStatisticOutput("sst.statOutputCSV", {"filepath" : "./spaghetti-test3.csv",
                                             "separator" : ", " } )

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

sst.enableAllStatisticsForComponentType("spaghetti.Spaghetti",
                                        {"type":"sst.HistogramStatistic",
                                        "minvalue" : "10",
                                        "binwidth" : "10",
                                        "numbins"  : "50",
                                        "IncludeOutOfBounds" : "1"})

# EOF
