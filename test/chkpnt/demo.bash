#!/bin/bash

sst --checkpoint-period=10ns --checkpoint-prefix=chkpt --add-lib-path=../../sst-bench/chkpnt chkpnt-test1.py

# This step requires using Ken's sst branch checkpoint-serobj to generate chkpt_schema.json
# cat chkpt_schema.json | c++filt -t > schema.json

./checkpoint_dump.py schema.json chkpt_10000000_999.sstcpt
