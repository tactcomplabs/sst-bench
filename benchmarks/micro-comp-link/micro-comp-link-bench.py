#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# micro-comp-link-bench.py
#

import os
import argparse
import sst

parser = argparse.ArgumentParser(description="Run MicroCompLink Test2")
parser.add_argument("--numCores", type=int, help="Number of cores to load", default=10)
parser.add_argument("--verbose", type=int, help="verbosity level", default=1)
args = parser.parse_args()


print("MicroCompLink Benchmark SST Simulation Configuration:")
for arg in vars(args):
  print("\t", arg, " = ", getattr(args, arg))

#-- common params
net_params = {
  "input_buf_size" : "2048B",
  "output_buf_size" : "2048B",
  "link_bw" : "100GB/s"
}
rtr_params = {
  "xbar_bw" : "100GB/s",
  "flit_size" : "8B",
  "num_ports" : args.numCores,
  "id" : 0
}

#-- create the router
router = sst.Component("router", "merlin.hr_router")
router.setSubComponent("topology", "merlin.singlerouter")
router.addParams(net_params)
router.addParams(rtr_params)

#-- create all the cores + links
for comp in range(args.numCores):
    core = sst.Component("c_" + str(comp), "microcomplink.MicroCompLink")
    core.addParams({
        "verbose" : args.verbose,
        "clock" : "1GHz",
    })
    nic = core.setSubComponent("nic", "microcomplink.MicroCompLinkNIC")
    iface = nic.setSubComponent("iface", "merlin.linkcontrol")
    iface.addParams(net_params)
    link = sst.Link("link_" + str(comp))
    link.connect( (iface, "rtr_port", "1us"), (router, "port"+str(comp), "1us") )

# EOF
