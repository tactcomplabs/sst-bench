#!/bin/bash
mkdir -p run
cd run

# cliControl
# 0b0100_0000 : 0x40  Every checkpoint
# 0b0010_0000 : 0x20  Every checkpoint when probe is active
# 0b0001_0000 : 0x10  Every checkpoint sync state change
# 0b0000_0100 : 0x04  Every probe sample
# 0b0000_0010 : 0x02  Every probe sample from trigger onward
# 0b0000_0001 : 0x01  Every probe state change
export CLI_CONTROL=64
export PROBE_PORT=10000
export PROBE_START_CYCLE=3000000
export PROBE_END_CYCLE=8000000
export PROBE_POST_DELAY=10
export PROBE_BUFFER_SIZE=1024
sst --checkpoint-sim-period=1us ../dbgcli-sanity.py &
sleep 2
../dbgcli-client.py <<EOF
echo hello there sst component
echo help
help
echo help cli_id
help cli_id
echo help component
help component
echo help cycle
help cycle
echo help disconnect
help disconnect
echo help echo
help echo
echo help hostname
help hostname
echo help probestate
help probestate
echo help run
help run
echo help spin
help spin
echo help syncstate
echo syncstate
echo run
run
echo disconnect
disconnect
EOF

wait

