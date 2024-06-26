#!/bin/bash


cpt=chkpt_20000_1

# genereate sstcpt files
sst --checkpoint-period=10ns --checkpoint-prefix=chkpt --add-lib-path=../../sst-bench/chkpnt chkpnt-test1.py

# requires Ken's sst branch checkpoint-serobj
cat chkpt_schema.json | c++filt -t > schema.json

# dump checkpoint information
./checkpoint_dump.py schema.json $cpt.sstcpt

# debug reference
hexdump -C $cpt.sstcpt > $cpt.hex


