#!/bin/bash

cpt=dbg_1000000_0

rm -f *.sstcpt *.json *.hex

# generate sstcpt files
sst --checkpoint-period=1000ns --checkpoint-prefix=dbg --gen-checkpoint-schema --add-lib-path=../../sst-bench/dbgproto dbgproto-test1.py

# requires Ken's sst branch checkpoint-serobj
cat $cpt.json | c++filt -t > ${cpt}_schema.json

# dump checkpoint information
./checkpoint_dump.py ${cpt}_schema.json $cpt.sstcpt

# debug reference
hexdump -C $cpt.sstcpt > $cpt.hex


