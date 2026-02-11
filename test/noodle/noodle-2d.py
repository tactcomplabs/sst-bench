#!/usr/bin/env python3

#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# 2dnoodle.py
#
# This is modified from sst-bench/test/grid/2d.py to test sst-sweeper.py

import argparse
import os
import sst

parser = argparse.ArgumentParser(description="noodle in two dimensions")
network_group = parser.add_argument_group('Network Configuration')
network_group.add_argument("--x", type=int, help="Number of horizonal components", default=2)
network_group.add_argument("--y", type=int, help="Number of vertical components", default=1)
comp_group = parser.add_argument_group('Component Configuration')
comp_group.add_argument("--rngSeed", type=int, help="Random number generator seed", default=2)
comp_group.add_argument("--clocks", type=int, help="Number of clocks to run sim", default=10000)
comp_group.add_argument("--clockFreq", type=int, help="Clock Frequency in GHz", default=1)
# comp_group.add_argument("--numPorts",  type=int, help="Number of ports", default=8)
comp_group.add_argument("--msgPerClock",  type=int, help="Messages per clock", default=3)
comp_group.add_argument("--bytesPerClock",  type=int, help="Bytes per clock", default=4)
comp_group.add_argument("--portsPerClock",  type=int, help="Ports per clock", default=4)
comp_group.add_argument("--verbose",  type=int, help="verbosity level", default=0)
args = parser.parse_args()

print("Noodle in Two Dimensions")
for arg in vars(args):
  print("\t", arg, " = ", getattr(args, arg))

# the number of ports must always be 8 but may change this later
PORTS = 8
SST_COMPONENT="noodle.Noodle"

comp_params = {
  "verbose"       : args.verbose,
  "clockFreq"     : f"{args.clockFreq}GHz",
  "numPorts"      : PORTS,
  "msgPerClock"   : args.msgPerClock,
  "bytesPerClock" : args.bytesPerClock,
  "portsPerClock" : args.portsPerClock,
  "clocks"        : args.clocks,
  "rngSeed"       : args.rngSeed
}

class GRIDNODE():
  def __init__(self, x, y):
    id = f"cp_{x}_{y}"
    self.id = id
    self.comp = sst.Component(id, SST_COMPONENT )
    self.comp.addParams(comp_params)
    # everyone gets 8 links, up/down/left/right, send/rcv
    # links here are associated with this component's send ports
    self.upLink = sst.Link(f"upLink_{x}_{y}")
    self.downLink = sst.Link(f"downLink_{x}_{y}")
    self.leftLink = sst.Link(f"leftLink_{x}_{y}")
    self.rightLink = sst.Link(f"rightLink_{x}_{y}")
    # identify neighborhood
    self.neighbor = {}
    self.neighbor['u']  = f"cp_{x}_{(y+1)%args.y}"
    self.neighbor['d']  = f"cp_{x}_{(y-1)%args.y}"
    self.neighbor['l']  = f"cp_{(x-1)%args.x}_{y}"
    self.neighbor['r']  = f"cp_{(x+1)%args.x}_{y}"

if args.x==2 and args.y==1:
  # for known good check
  cp0 = sst.Component("cp0", SST_COMPONENT)
  cp0.addParams(comp_params)
  cp1 = sst.Component("cp1", SST_COMPONENT)
  cp1.addParams(comp_params)
  link = [None] * PORTS
  for i in range(0, PORTS):
      # print(f"Creating link {i}")
      link[i] = sst.Link(f"link{i}")
      link[i].connect( (cp0, f"port{i}", "1us"), (cp1, f"port{i}", "1us") )
else:
  # create grid components
  grid = {}
  for x in range(args.x):
    for y in range(args.y):
      comp = GRIDNODE(x,y)
      grid[comp.id] = comp

  # connect send ports to adjacent rcv ports. Edge nodes wrap around
  #  send: up=0, down=1, left=2, right=3
  #  rcv:  up=4, down=5, left=6, right=7
  for node in grid:
    # print(f"Connecting {node}")
    tile = grid[node]
    comp=tile.comp
    tile.upLink.connect(    (comp, f"port{0}", "1us"), (grid[tile.neighbor['u']].comp, f"port{5}", "1us") )
    tile.downLink.connect(  (comp, f"port{1}", "1us"), (grid[tile.neighbor['d']].comp, f"port{4}", "1us") )
    tile.leftLink.connect(  (comp, f"port{2}", "1us"), (grid[tile.neighbor['l']].comp, f"port{7}", "1us") )
    tile.rightLink.connect( (comp, f"port{3}", "1us"), (grid[tile.neighbor['r']].comp, f"port{6}", "1us") )

# EOF
