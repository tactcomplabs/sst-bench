#!/bin/bash
#
# Unregisters sstbench libs from the SST infrastructure
#

#-- unregister the libs
sst-register -u msgperf

#-- forcible remove it from the local script
CONFIG=~/.sst/sstsimulator.conf
if test -f "$CONFIG"; then
  echo "Removing configuration from local config=$CONFIG"
  sed -i.bak '/msgperf/d' $CONFIG
fi

# EOF
