#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# restart-test1.py
#

import os
import sst

rt0 = sst.Component("rt0", "restart.Restart")
rt0.addParams({
  "verbose" : 5,
  "numBytes" : "1MiB",
  "clocks" : 10000,
  "baseSeed" : 1223,
  "clockFreq" : "1Ghz"
})


# EOF
