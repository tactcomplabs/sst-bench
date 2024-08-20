#
# Copyright (C) 2017-2024 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details
#
# dbgcli-test1.py
#

import os
import sst

# PROBE controls
PROBE_MODE = 1
PROBE_START_CYCLE = int(os.getenv("PROBE_START_CYCLE", 0))
PROBE_END_CYCLE = int(os.getenv("PROBE_END_CYCLE", 0))
PROBE_BUFFER_SIZE = int(os.getenv("PROBE_BUFFER_SIZE", 16))
PROBE_POST_DELAY  = int(os.getenv("PROBE_POST_DELAY", 8))

# Interactive mode controls
PROBE_PORT = int(os.getenv("PROBE_PORT", 0))

# cliControl determines when to break into interactive mode
# 0b0100_0000 : 0x40 : 64 Every checkpoint
# 0b0010_0000 : 0x20 : 32 Every checkpoint when probe is active
# 0b0001_0000 : 0x10 : 16 Every checkpoint sync state change
# 0b0000_0100 : 0x04 : 04 Every probe sample
# 0b0000_0010 : 0x02 : 02 Every probe sample from trigger onward
# 0b0000_0001 : 0x01 : 01 Every probe state change

CLI_CONTROL = int(os.getenv("CLI_CONTROL", 0))

# Component custom trace controls
TRACE_SEND = 1
TRACE_RECV = 2

MIN_DATA = 1
MAX_DATA = 100

VERBOSE = int(os.getenv("VERBOSE", 1))

cp0 = sst.Component("cp0", "dbgcli.DbgCLI")
cp0.addParams({
  "verbose" : VERBOSE,
  "numPorts" : 1,
  "minData" : MIN_DATA,
  "maxData" : MAX_DATA,
  "clockDelay" : 100,
  "clocks" : 10000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz",
  # common probe controls
  #"probeMode" : 1,
  "probeStartCycle" : PROBE_START_CYCLE,
  "probeEndCycle"   : PROBE_END_CYCLE,
  "probeBufferSize" : PROBE_BUFFER_SIZE,
  "probePostDelay"  : PROBE_POST_DELAY,
  "probePort"       : PROBE_PORT,
  "cliControl"      : CLI_CONTROL,
  # component specific probe controls
  "traceMode"       : TRACE_RECV,
})

cp1 = sst.Component("cp1", "dbgcli.DbgCLI")
cp1.addParams({
  "verbose" : VERBOSE,
  "numPorts" : 1,
  "minData" : MIN_DATA,
  "maxData" : MAX_DATA,
  "clockDelay" : 100,
  "clocks" : 10000,
  "rngSeed" : 1223,
  "clockFreq" : "1Ghz",
  # common probe controls
  "probeMode" : 1,
  "probeStartCycle" : PROBE_START_CYCLE,
  "probeEndCycle"   : PROBE_END_CYCLE,
  "probeBufferSize" : PROBE_BUFFER_SIZE,
  "probePostDelay"  : PROBE_POST_DELAY,
   #"probePort" : PROBE_PORT+1,
   #"cliControl"     : CLI_CONTROL,
   # component specific probe controls
   "traceMode"      : TRACE_SEND,
})

link0 = sst.Link("link0")
link0.connect( (cp0, "port0", "1us"), (cp1, "port0", "1us") )

# EOF
