# List all test names here
ALL_TESTS = basic.0.0 basic.0.1
# 

# Repository root
PROJHOME ?= $(realpath ../..)

# SST
SSTCFG ?= $(PWD)/basic.py
SSTOPTS += --add-lib-path=$(PROJHOME)/sst-bench/dbgcli --output-json=rank.json
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
$(OUTDIR)/basic.0.0/run.log:      SSTOPTS += --checkpoint-sim-period=1us
$(OUTDIR)/basic.0.1/run.log:      SSTOPTS += --checkpoint-sim-period=500ns
$(OUTDIR)/basic.0.1/run.log:      ENVOPTS += VERBOSE=10


# TODO does --output-directory actually work in sst? Post a bug if no
# Run command
%.log: $(SSTCFG)
	@mkdir -p $(@D)
	@echo Running $(basename $@) in $(@D)
	( cd $(@D) && $(ENVOPTS) $(MPIOPTS) $(SST) $(SSTOPTS) $(SSTCFG) \
 > run.log && (echo "pass" > run.status; $(DOT2PDF)) || echo "fail" > run.status )
	@echo "### " $@":" `cat $(@D)/run.status`

clean:
	rm -rf $(OUTDIR)

help:
	@echo make run
	@echo make TLIST=\"test1 test2 ...\"
	@echo make 
	@echo make DOT=1 SSTCFG=\$$PWD/test3.py TLIST=test3
	@echo make VALGRIND=1 TLIST=test1
	@echo Valid TLIST selections are: $(ALL_TESTS)
	@echo

.PHONY: clean help

.SECONDARY:

.PRECIOUS: %.log

#-- EOF

