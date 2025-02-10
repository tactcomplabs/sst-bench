#!/bin/bash
#
# Unregisters sstbench libs from the SST infrastructure
#

#-- unregister the libs
sst-register -u msgperf
sst-register -u microcomp
sst-register -u chkpnt
sst-register -u grid
sst-register -u largestat
sst-register -u largestatchkpnt
sst-register -u microcomplink
sst-register -u restart
sst-register -u restore
sst-register -u tcldbg

#-- forcible remove it from the local script
CONFIG=~/.sst/sstsimulator.conf
if test -f "$CONFIG"; then
  echo "Removing configuration from local config=$CONFIG"
  sed -i.bak '/msgperf/d' $CONFIG
  sed -i.bak '/microcomp/d' $CONFIG
  sed -i.bak '/chkpnt/d' $CONFIG
  sed -i.bak '/grid/d' $CONFIG
  sed -i.bak '/largestat/d' $CONFIG
  sed -i.bak '/largestatchkpnt/d' $CONFIG
  sed -i.bak '/microcomplink/d' $CONFIG
  sed -i.bak '/restart/d' $CONFIG
  sed -i.bak '/restore/d' $CONFIG
  sed -i.bak '/tcldbg/d' $CONFIG
fi

# EOF
