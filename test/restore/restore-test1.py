#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# restore-test1.py
#

import os
import sst

rp0 = sst.Component("rp0", "restore.Restore")
rp0.addParams({
  "verbose" : 5,
  "numBytes" : "1MiB",
  "clocks" : 10000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz"
})


# EOF
