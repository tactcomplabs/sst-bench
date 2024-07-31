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
  "maxData" : 10000,
  "clockDelay" : 10,
  "clocks" : 10000000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz"
})

cp1 = sst.Component("t1", "tcldbg.TclDbg")
cp1.addParams({
  "verbose" : 5,
  "minData" : 1,
  "maxData" : 10000,
  "clockDelay" : 10,
  "clocks" : 10000000,
  "rngSeed" : 1227,
  "clockFreq" : "1Ghz"
})

#sst.enableAllStatisticsForComponentType("tcldbg.TclDbg",
#    {"type":"sst.HistogramStatistic",
#     "minvalue" : "10",
#     "binwidth" : "10",
#     "numbins"  : "100",
#     "IncludeOutOfBounds" : "1"})

sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV")
#sst.enableAllStatisticsForAllComponents()
sst.enableStatisticForComponentType("tcldbg.TclDbg",
    "statBytes",
        {"type":"sst.HistogramStatistic",
         "minvalue" : "0",
         "numbins" : "100",
         "binwidth" : "100"})

sst.enableStatisticForComponentType("tcldbg.TclDbg",
    "statTiming",
        {"type":"sst.HistogramStatistic",
         "minvalue" : "0",
         "numbins" : "100",
         "binwidth" : "1000"})

# EOF
