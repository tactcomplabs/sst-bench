# List all test names here
ALL_TESTS  = basic.0.0 basic.0.1 basic.0.2 basic.0.3
ALL_TESTS += basic.0.4 basic.0.5 basic.0.6 basic.0.7

# Tests development
WIP_TESTS += cli0x40.0 cli0x20.0 cli0x10.0
WIP_TESTS += cli0x04.0 cli0x02.0 cli0x01.0

# Repository root
PROJHOME ?= $(realpath ../..)

# SST
SSTCFG ?= $(PWD)/probe.py
SSTCHKPT ?= --checkpoint-sim-period=1us
SSTOPTS += $(SSTCHKPT) --add-lib-path=$(PROJHOME)/sst-bench/dbgcli --output-json=rank.json
ifdef VALGRIND
 SST ?= valgrind sst
else
 SST = sst
endif

# MPI
ifdef MPI_RANKS
 MPIOPTS ?= mpirun -n $(MPI_RANKS) --use-hwthread-cpus
 SSTOPTS += --parallel-output=1
endif

# Graph PDF
ifdef DOT
SSTOPTS += --output-dot=run.dot --dot-verbosity=10
DOT2PDF = dot -Tpdf run.dot -o run.pdf
endif

# Output Directories
OUTDIR = out

# Final test selection
TLIST ?= $(ALL_TESTS)

# Targets
LOGS   := $(addsuffix /run.log,$(addprefix $(OUTDIR)/,$(TLIST)))
TARGS  := $(LOGS)

# Recipes
all: $(TARGS)
run: $(LOGS)

#
# Customize environment and command line options on per test basis here
#

# basic test defaults
# sst checkpoint sampling period: 1us
# sample:  		cp1 send events, cp0 recv events
# trigger:  	max payload size
# 
# PROBE_CP0=0 (probeMode=0)
# PROBE_CP1=0 (probeMode=0)
# PROBE_START_CYCLE=0  (probeStartCycle=0)   # start of 1st checkpoint
# PROBE_END_CYCLE=0    (probeEndCycle=0)     # no limit
# PROBE_BUFFER_SIZE=16 (probeBufferSize=16)
# PROBE_POST_DELAY=8   (probePostDelay=8)
# PROBE_PORT=10000     (probePort=10000)     # cp0 10000, cp1 10001, ...
# CLI_CONTROL_CP0=0    (cliControl=0) 
# CLI_CONTROL_CP1=0    (cliControl=0) 

# cliControl determines when to break into interactive mode
# 0b0100_0000 : 0x40 : 64 Every checkpoint
# 0b0010_0000 : 0x20 : 32 Every checkpoint when probe is active
# 0b0001_0000 : 0x10 : 16 Every checkpoint sync state change
# 0b0000_0100 : 0x04 : 04 Every probe sample
# 0b0000_0010 : 0x02 : 02 Every probe sample from trigger onward
# 0b0000_0001 : 0x01 : 01 Every probe state change
# 0b0000_0000 : 0x00 : 00 Disabled

# For testing always have PROBE_CP0 and PROBE_CP1 enabled
ENVOPTS = PROBE_CP0=1 PROBE_CP1=1 

# Test: basic.0.* : check trigger and buffering
$(OUTDIR)/basic.0.0/run.log:   ENVOPTS += PROBE_BUFFER_SIZE=4 PROBE_POST_DELAY=0
$(OUTDIR)/basic.0.1/run.log:   ENVOPTS += PROBE_BUFFER_SIZE=4 PROBE_POST_DELAY=1
$(OUTDIR)/basic.0.2/run.log:   ENVOPTS += PROBE_BUFFER_SIZE=4 PROBE_POST_DELAY=2
$(OUTDIR)/basic.0.3/run.log:   ENVOPTS += PROBE_BUFFER_SIZE=4 PROBE_POST_DELAY=3
$(OUTDIR)/basic.0.4/run.log:   ENVOPTS += PROBE_BUFFER_SIZE=4 PROBE_POST_DELAY=4
$(OUTDIR)/basic.0.5/run.log:   ENVOPTS += PROBE_BUFFER_SIZE=4 PROBE_POST_DELAY=5
$(OUTDIR)/basic.0.6/run.log:   ENVOPTS += PROBE_BUFFER_SIZE=4 PROBE_POST_DELAY=6
$(OUTDIR)/basic.0.7/run.log:   ENVOPTS += PROBE_BUFFER_SIZE=4 PROBE_POST_DELAY=7

# Test: cli0x40.* : check break to CLI at every checkpoint
$(OUTDIR)/cli0x40.0/run.log:   ENVOPTS += PROBE_START_CYCLE=3000000 CLI_CONTROL_CP1=64
$(OUTDIR)/cli0x20.0/run.log:   ENVOPTS += PROBE_START_CYCLE=3000000 CLI_CONTROL_CP1=32
$(OUTDIR)/cli0x10.0/run.log:   ENVOPTS += PROBE_START_CYCLE=3000000 CLI_CONTROL_CP1=16
$(OUTDIR)/cli0x04.0/run.log:   ENVOPTS += PROBE_START_CYCLE=3000000 CLI_CONTROL_CP1=4
$(OUTDIR)/cli0x02.0/run.log:   ENVOPTS += PROBE_START_CYCLE=3000000 CLI_CONTROL_CP1=2
$(OUTDIR)/cli0x01.0/run.log:   ENVOPTS += PROBE_START_CYCLE=3000000 CLI_CONTROL_CP1=1  

# TODO does --output-directory actually work in sst? Post a bug if no
# Run command
%.log: $(SSTCFG)
	@mkdir -p $(@D)
	@echo Running $(basename $@) in $(@D)
	( cd $(@D) && $(ENVOPTS) $(MPIOPTS) $(SST) $(SSTOPTS) $(SSTCFG) > run.log && (echo "pass" > run.status; $(DOT2PDF)) || echo "fail" > run.status )
	@echo "### " $@":" `cat $(@D)/run.status`

RUNSCRIPT ?= $(PWD)/client-run5.bash

# experimental: attach client
# %.log: $(SSTCFG)
# 	@mkdir -p $(@D)
# 	@echo Running $(basename $@) in $(@D)
# 	( cd $(@D) && $(ENVOPTS) $(MPIOPTS) SST="$(SST)" SSTOPTS="$(SSTOPTS)" SSTCFG=$(SSTCFG) $(RUNSCRIPT) > run.log && (echo "pass" > run.status; $(DOT2PDF)) || echo "fail" > run.status )
# 	@echo "### " $@":" `cat $(@D)/run.status`

check: run
	diff -r out logs | grep -v 'Real CPU time' | grep -v Binary | egrep -v '^\-\-\-$$' | egrep -v '^\d+c\d+$$' | egrep -v '^\d+,\d+c\d+,\d+$$' | egrep -v 'Only in out/.+: checkpoint'

clean:
	rm -rf $(OUTDIR)

help:
	@echo make run
	@echo make check
	@echo make TLIST=\"test1 test2 ...\"
	@echo make 
	@echo make DOT=1 SSTCFG=\$$PWD/test3.py TLIST=test3
	@echo make VALGRIND=1 TLIST=test1
	@echo Valid TLIST selections are:
	@echo $(ALL_TESTS)
	@echo WIP TLIST selections are:
	@echo $(WIP_TESTS)
	@echo

.PHONY: clean help

.SECONDARY:

.PRECIOUS: %.log

#-- EOF

