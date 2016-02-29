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

PROGRAMS=

M4PROGRAMS=\
	pscheduler

COMMANDS=\
	task

M4COMMANDS=\
	internal

ALLPROGRAMS=$(PROGRAMS) $(M4PROGRAMS)
ALLCOMMANDS=$(COMMANDS) $(M4COMMANDS)

ALLM4=$(M4PROGRAMS) $(M4COMMANDS)
ALLM4=$(ALLM4:%=%.m4)

ALL=$(PROGRAMS) $(M4PROGRAMS) $(COMMANDS) $(M4COMMANDS)

default:  build

%: %.m4
ifndef COMMANDSINSTALLED
	@echo No COMMANDSINSTALLED specified for build of $@
	@false
else
	m4 -D__COMMANDS__=$(COMMANDSINSTALLED) $< > $@
endif


build: $(ALL)
TO_CLEAN += $(M4PROGRAMS) $(M4COMMANDS)


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
	echo $(ALLPROGRAMS) AP
	install -m 555 $(ALLPROGRAMS) $(BINDIR)
	mkdir -p $(COMMANDSDIR)
	install -m 555 $(ALLCOMMANDS) $(COMMANDSDIR)


clean:
	rm -rf $(TO_CLEAN) *~
