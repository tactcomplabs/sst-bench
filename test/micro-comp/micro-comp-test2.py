#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# micro-comp-test2.py
#

import os
import argparse
import sst


parser = argparse.ArgumentParser(description="Run MicroComp Test2")
parser.add_argument("--numComps", type=int, help="Number of components to load", default=1)
args = parser.parse_args()

print("MicroComp Test 2 SST Simulation Configuration:")
for arg in vars(args):
  print("\t", arg, " = ", getattr(args, arg))

for comp in range(args.numComps):
  comp = sst.Component("c_" + str(comp), "microcomp.MicroComp")
  comp.addParams({"verbose" : 0})

# EOF
