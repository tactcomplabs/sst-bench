#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# large-stat-chkpnt-test2.py
#

import os
import argparse
import sst

parser = argparse.ArgumentParser(description="Run LargeStatChkpnt Test2")
parser.add_argument("--numComps", type=int, help="Number of cores to load", default=1)
parser.add_argument("--numClocks", type=int, help="Number of clocks to run", default=100000000)
parser.add_argument("--numStats", type=int, help="Number of stats to load", default=1)
parser.add_argument("--verbose", type=int, help="verbosity level", default=1)
args = parser.parse_args()


print("LargeStatChkpnt Test 2 SST Simulation Configuration:")
for arg in vars(args):
  print("\t", arg, " = ", getattr(args, arg))

#-- create all the cores + links
for comp in range(args.numComps):
    core = sst.Component("c_" + str(comp), "largestatchkpnt.LargeStatChkpnt")
    core.addParams({
        "verbose" : args.verbose,
        "numStats" : args.numStats,
        "numClocks" : args.numClocks,
    })

sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {"filepath" : "./large-stat-chkpnt-test2.csv"})
sst.enableAllStatisticsForAllComponents()
# EOF
