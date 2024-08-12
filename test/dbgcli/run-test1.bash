#!/bin/bash
mkdir -p run
cd run

export PROBE_PORT=12345
export PROBE_START_CYCLE=5000000
export PROBE_POST_DELAY=10
export PROBE_BUFFER_SIZE=1024
sst --checkpoint-sim-period=1us ../dbgcli-test1.py &
sleep 2
../run-client.py <<EOF
echo hello there sst component
echo 1
echo 2
echo 3
disconnect
EOF

wait

