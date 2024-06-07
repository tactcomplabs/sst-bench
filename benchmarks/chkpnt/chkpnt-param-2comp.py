#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# chkpnt-param.py
#

import os
import argparse
import sst

parser = argparse.ArgumentParser(description="Run chkpnt-param-2comp")
parser.add_argument("--numPorts", type=int, help="Number of ports per component", default=1)
parser.add_argument("--minData", type=int, help="Minimum number of unsigned data elements", default=1)
parser.add_argument("--maxData", type=int, help="Maximum number of unsigned data elements", default=2)
parser.add_argument("--clockDelay", type=int, help="Clock delay between sends", default=100)
parser.add_argument("--clocks", type=int, help="Executable clock cycles", default=1000)
parser.add_argument("--rngSeed", type=int, help="RNG seed", default=1223)
parser.add_argument("--clockFreq", help="Clock frequency", default="1GHz")
args = parser.parse_args()

print("chkpnt-param-2comp SST Simulation Configuration:")
for arg in vars(args):
  print("\t", arg, " = ", getattr(args, arg))

cp_params = {
    "verbose" : 0,
    "numPorts" : args.numPorts,
    "minData" : args.minData,
    "maxData" : args.maxData,
    "clockDelay" : args.clockDelay,
    "clocks" : args.clocks,
    "rngSeed" : args.rngSeed,
    "clockFreq" : args.clockFreq,
}

cp0 = sst.Component("cp0", "chkpnt.Chkpnt")
cp0.addParams(cp_params)

cp1 = sst.Component("cp1", "chkpnt.Chkpnt")
cp1.addParams(cp_params)

for port in range(args.numPorts):
    link = sst.Link("link"+str(port))
    link.connect( (cp0, "port"+str(port), "1us"), (cp1, "port"+str(port), "1us") )


# EOF
