#!/bin/bash
#
# Derives the SST major version
# In SST 14.0.0.kg; this script returns "14.0.0.kg"
#

sst --version | awk '{print $3}' | tr -d '()'

# EOF
