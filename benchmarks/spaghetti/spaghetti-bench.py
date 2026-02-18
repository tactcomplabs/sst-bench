#!/usr/bin/env python3
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# spaghetti-bench.py
#
#

import sys
import os
import argparse
import random
import sst

parser = argparse.ArgumentParser(description="Spaghetti Bench")
parser.add_argument("--verbose", type=int, help="Verbosity", default=0)
parser.add_argument("--numComps", type=int, help="Number of Spaghetti components", default=2)
parser.add_argument("--portsPerComp", type=int, help="Number of ports per component", default=2)
parser.add_argument("--msgsPerPort", type=int, help="Number of msgs to inject per port", default=100)
parser.add_argument("--bytesPerMsg", type=int, help="Number of bytes per message", default=64)
parser.add_argument("--rngSeed", type=int, help="RNG seed value", default=3131)
args = parser.parse_args()

print("Spaghetti-Bench test SST Simulation Configuration:")
for arg in vars(args):
    print("\t", arg, " = ", getattr(args, arg))

if args.numComps % 2 != 0:
    print(f"Spaghetti-Bench requires an even number of components!")
    sys.exit(-1)

if args.portsPerComp % 2 != 0:
    print(f"Spaghetti-Bench requires an even number of ports per component!")
    sys.exit(-1)

# create all the components
endpoints = []
for comp in range(args.numComps):
    c = sst.Component("s"+str(comp), "spaghetti.Spaghetti")
    c.addParams({
        "verbose": args.verbose,
        "numPorts" : args.portsPerComp,
        "numMsgs" : args.msgsPerPort,
        "bytesPerMsg" : args.bytesPerMsg,
        "rngSeed" : args.rngSeed
    })
    endpoints.append(c)

# setup a ring network of links
# 50% of the links for each component go to the Nth+1 component
# 50% of the links for each component go to the Nth-1 component
for compLink in range(1, args.numComps):
    # lower 50%
    upperLink = args.portsPerComp-1
    for lowerLink in range(0, int(args.portsPerComp/2)):
        link = sst.Link("link_s" + str(compLink) + "p" + str(lowerLink) + "p" + str(upperLink))
        link.connect( (endpoints[compLink],  "port"+str(lowerLink), "1us"),
                      (endpoints[compLink-1],"port"+str(upperLink), "1us") )
        upperLink = upperLink - 1

# handle lowers links for component 0
upperLink = args.portsPerComp-1
for lowerLink in range(0, int(args.portsPerComp/2)):
    link = sst.Link("link_s0p" + str(lowerLink) + "p" + str(upperLink))
    link.connect( (endpoints[0], "port"+str(lowerLink), "1us"),
                  (endpoints[args.numComps-1], "port"+str(upperLink), "1us") )
    upperLink = upperLink - 1


