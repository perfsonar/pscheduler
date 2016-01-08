#
# Makefile for pScheduler Core
#

#
# The following variables need to be specified when running this
# Makefile:
#
#   BINDIR              Where binaries should be installed (e.g., /usr/bin)
#   COMMANDSDIR         Where command programs should be installed
#   COMMANDSINSTALLED   Where $(COMMANDSDIR) is when installed
#

PROGRAMS=\
	pscheduler

COMMANDS=\
	internal

ALL=$(PROGRAMS) $(COMMANDS)
ALLM4=$(ALL:%=%.m4)

default:  build

%: %.m4
ifndef COMMANDSINSTALLED
	@echo No COMMANDSINSTALLED specified for build of $@
	@false
else
	m4 -D__COMMANDS__=$(COMMANDSINSTALLED) $< > $@
endif


build: $(ALL)
TO_CLEAN += $(ALL)


install: $(ALL)
ifndef BINDIR
	@echo No BINDIR specified for installation
	@false
endif
ifndef COMMANDSDIR
	@echo No COMMANDSDIR specified for installation
	@false
endif
	mkdir -p $(BINDIR)
	install -m 555 $(PROGRAMS) $(BINDIR)
	mkdir -p $(COMMANDSDIR)
	install -m 555 $(COMMANDS) $(COMMANDSDIR)


clean:
	rm -rf $(TO_CLEAN) *~
