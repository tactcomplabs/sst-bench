#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# msg-perf-test2.py
#

import os
import argparse
import sst

parser = argparse.ArgumentParser(description="Run MsgPerf Test2")
parser.add_argument("--numCores", type=int, help="Number of cores to load", default=2)
parser.add_argument("--startSize", help="starting payload size", default="64B")
parser.add_argument("--endSize", help="ending payload size", default="128B")
parser.add_argument("--stepSize", help="step size", default="8B")
parser.add_argument("--clockDelay", type=int, help="clokc delay", default=100)
parser.add_argument("--iters", type=int, help="iterations per clock", default=1)
parser.add_argument("--verbose", type=int, help="verbosity level", default=1)
args = parser.parse_args()


print("MsgPerf Test 2 SST Simulation Configuration:")
for arg in vars(args):
  print("\t", arg, " = ", getattr(args, arg))

#-- common params
nic_params = {
  "verbose" : args.verbose
}

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
    core = sst.Component("c_" + str(comp), "msgperf.MsgPerfCPU")
    core.addParams({
        "verbose" : args.verbose,
        "clock" : "1GHz",
        "startSize" : args.startSize,
        "endSize" : args.endSize,
        "stepSize" : args.stepSize,
        "iters" : args.iters,
        "clockDelay" : args.clockDelay
    })
    nic = core.setSubComponent("nic", "msgperf.MsgPerfNIC")
    nic.addParams(nic_params)
    iface = nic.setSubComponent("iface", "merlin.linkcontrol")
    iface.addParams(net_params)
    link = sst.Link("link_" + str(comp))
    link.connect( (iface, "rtr_port", "1us"), (router, "port"+str(comp), "1us") )

sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {"filepath" : "./msg-perf-test2.csv"})
sst.enableAllStatisticsForAllComponents()
# EOF
