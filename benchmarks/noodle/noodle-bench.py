#!/usr/bin/env python3
#
# Copyright (C) 2017-2025 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# noodle-bench.py
#
#

import os
import argparse
import random
import sst

parser = argparse.ArgumentParser(description="Noodle Bench")
parser.add_argument("--verbose", type=int, help="Verbosity", default=0)
parser.add_argument("--numComps", type=int, help="Number of Noodle components", default=2)
parser.add_argument("--portsPerComp", type=int, help="Number of ports per component", default=2)
parser.add_argument("--msgPerClock", type=int, help="Messages per clock cycle", default=2)
parser.add_argument("--bytesPerClock", type=int, help="Bytes per clock", default=4)
parser.add_argument("--clocks", type=int, help="Number of clock cycles to execute", default=1000000)
parser.add_argument("--rngSeed", type=int, help="RNG Seed", default=3131)
args = parser.parse_args()

print("Noodle-Bench test SST Simulation Configuration:")
for arg in vars(args):
    print("\t", arg, " = ", getattr(args, arg))

# build the endpoint list
endpoints = []
for comp in range(args.numComps):
    c = sst.Component("n"+str(comp), "noodle.Noodle")
    c.addParams({
        "verbose" : args.verbose,
        "clockFreq" : "1GHz",
        "numPorts" : args.portsPerComp,
        "msgPerClock" : args.msgPerClock,
        "bytesPerClock" : args.bytesPerClock,
        "clocks" : args.clocks,
        "rngSeed" : args.rngSeed
    })

    for port in range(args.portsPerComp):
        ltuple = (c, "n" + str(comp), port)
        endpoints.append(ltuple)

if len(endpoints) % 2 != 0:
    print(f"Warning: Odd number of endpoints ({len(endpoints)}). Removing one.")
    endpoints.pop()
#print("Noodle-Bench endpoint list")
#print(endpoints)

# randomly select two endpoints to connect
while len(endpoints) >= 2:
    random.shuffle(endpoints)
    end1 = endpoints.pop()
    end2 = endpoints.pop()

    #print(f"Connecting endpoints: {end1} : {end2}")

    link = sst.Link("link_" + str(end1[1]) + "p" + str(end1[2]) + "_" +
                    str(end2[1]) + "p" + str(end2[2]))
    link.connect( (end1[0], "port"+str(end1[2]), "1us"),
                    (end2[0], "port"+str(end2[2]), "1us") )

# EOF
