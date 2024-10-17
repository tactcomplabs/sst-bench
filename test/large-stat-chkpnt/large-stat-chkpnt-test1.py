#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# large-stat-chckpnt-test1.py
#

import os
import sst

c0 = sst.Component("c0", "largestatchkpnt.LargeStatChkpnt")
c0.addParams({
  "verbose" : 5,
  "numStats" : 10,
  "numClocks" : 100000000,
})

# EOF
