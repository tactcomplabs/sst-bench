#!/bin/bash -x
#
# Copyright (C) 2017-2026 Tactical Computing Laboratories, LLC
# All Rights Reserved
# contact@tactcomplabs.com
#
# See LICENSE in the top level directory for licensing details

/bin/rm -rf crcr_*

ADDLIBPATH="--add-lib-path=../../components/noodle"
if [ "$SST_VALGRIND" -eq 1 ]; then
    SST="valgrind sst"
else
    SST="sst"
fi    

# initial checkpoint
$SST --checkpoint-sim-period=3us --checkpoint-prefix=crcr_1_cpt noodle-2d.py || exit 1

# load checkpoint and generate new ones
$SST --checkpoint-sim-period=2us --checkpoint-prefix=crcr_2_rst_cpt  crcr_1_cpt/crcr_1_cpt_1_3000000/crcr_1_cpt_1_3000000.sstcpt || exit 2

# load all the checkpoints
$SST  ${ADDLIBPATH}  crcr_2_rst_cpt/crcr_2_rst_cpt_1_4000000/crcr_2_rst_cpt_1_4000000.sstcpt  || exit 31
$SST  ${ADDLIBPATH}  crcr_2_rst_cpt/crcr_2_rst_cpt_2_6000000/crcr_2_rst_cpt_2_6000000.sstcpt  || exit 32
$SST  ${ADDLIBPATH}  crcr_2_rst_cpt/crcr_2_rst_cpt_3_8000000/crcr_2_rst_cpt_3_8000000.sstcpt  || exit 33
$SST  ${ADDLIBPATH} crcr_2_rst_cpt/crcr_2_rst_cpt_4_10000000/crcr_2_rst_cpt_4_10000000.sstcpt || exit 34

/bin/rm -rf crcr_*
echo "run-cpt-rstcpt-rst.sh passed"
wait

