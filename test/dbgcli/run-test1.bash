#!/bin/bash
mkdir -p run
cd run

export DEBUG_PORT=12345
PROBE_START_CYCLE=6000000 sst --checkpoint-sim-period=1us ../dbgcli-test1.py &
sleep 2
../run-client.py <<EOF
echo hello there sst component
echo 1
echo 2
echo 3
disconnect
EOF

wait

