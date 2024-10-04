#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# 2d.py
#

import argparse
import os
import sst

parser = argparse.ArgumentParser(description="2d grid network test 1 with checkpoint/restart checks")
parser.add_argument("--numEdgePorts", type=int, help="Number of ports per component edge", default=10)
parser.add_argument("--verbose", type=int, help="verbosity level", default=5)
args = parser.parse_args()

print("2d grid test SST Simulation Configuration:")
for arg in vars(args):
  print("\t", arg, " = ", getattr(args, arg))

comp_params = {
  "verbose" : args.verbose,
  "numPorts" : args.numEdgePorts,
  "minData" : 1,
  "maxData" : 10000,
  "clockDelay" : 100,
  "clocks" : 10000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz"
}


cp0 = sst.Component("cp0", "grid.GridComp")
cp0.addParams(comp_params)

cp1 = sst.Component("cp1", "grid.GridComp")
cp1.addParams(comp_params)

link = [None] * args.numEdgePorts
for i in range(0,args.numEdgePorts):
    print(f"Creating link {i}")
    link[i] = sst.Link(f"link{i}")
    link[i].connect( (cp0, f"port{i}", "1us"), (cp1, f"port{i}", "1us") )

# EOF
