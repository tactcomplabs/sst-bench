#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# single-thread-restore.py
#

import os
import argparse
import sst

#--model-options="--numComps $COMPS --numKB $BASE"
parser = argparse.ArgumentParser(description="Run Single-Thread-Restore")
parser.add_argument("--numComps", type=int, help="Number of comps to load", default=1)
parser.add_argument("--numKB", help="number of KB of the payload", default="64KB")
args = parser.parse_args()

print("Single-Thread-Restore Test Configuration:")
for arg in vars(args):
  print("\t", arg, " = ", getattr(args, arg))


params = {
    "numBytes" : args.numKB+"KB",
    "clocks" : 10000
}

for comp in range(args.numComps):
    c = sst.Component("c_" + str(comp), "restore.Restore")
    c.addParams(params)
