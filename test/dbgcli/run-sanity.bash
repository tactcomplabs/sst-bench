#!/bin/bash
mkdir -p run
cd run

export PROBE_PORT=12345
export PROBE_START_CYCLE=5000000
export PROBE_END_CYCLE=7000000
export PROBE_POST_DELAY=10
export PROBE_BUFFER_SIZE=1024
sst --checkpoint-sim-period=1us ../dbgcli-sanity.py &
sleep 2
../dbgcli-client.py <<EOF
echo hello there sst component
echo help
help
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
echo help run
help run
echo help step
help step
echo help spin
help spin
echo run
run
echo step
step
echo disconnect
disconnect
EOF

wait

