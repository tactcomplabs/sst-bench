#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# micro-comp-link-test1.py
#

import os
import sst

cpu0 = sst.Component("cpu0", "microcomplink.MicroCompLink")
cpu0.addParams({
  "verbose" : 10,
  "clock" : "1GHz",
})
cpu1 = sst.Component("cpu1", "microcomplink.MicroCompLink")
cpu1.addParams({
  "verbose" : 10,
  "clock" : "1GHz",
})

nic0 = cpu0.setSubComponent("nic", "microcomplink.MicroCompLinkNIC")
nic1 = cpu1.setSubComponent("nic", "microcomplink.MicroCompLinkNIC")

iface0 = nic0.setSubComponent("iface", "merlin.linkcontrol")
iface1 = nic1.setSubComponent("iface", "merlin.linkcontrol")

router = sst.Component("router", "merlin.hr_router")
router.setSubComponent("topology", "merlin.singlerouter")

net_params = {
  "input_buf_size" : "2048B",
  "output_buf_size" : "2048B",
  "link_bw" : "100GB/s"
}
rtr_params = {
  "xbar_bw" : "100GB/s",
  "flit_size" : "8B",
  "num_ports" : "2",
  "id" : 0
}

iface0.addParams(net_params)
iface1.addParams(net_params)
router.addParams(net_params)
router.addParams(rtr_params)

link0 = sst.Link("link0")
link0.connect( (iface0, "rtr_port", "1us"), (router, "port0", "1us") )
link1 = sst.Link("link1")
link1.connect( (iface1, "rtr_port", "1us"), (router, "port1", "1us") )

# EOF