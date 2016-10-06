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
#   INTERNALSDIR         Where internal programs should be installed
#   INTERNALSINSTALLED   Where $(INTERNALSDIR) is when installed
#   TOOLCONFIGDIR       Where tool configuration files live
#

PROGRAMS=

M4PROGRAMS=\
	pscheduler

COMMANDS=\
	cancel \
	result \
	schedule \
	monitor \
	task \
	watch

M4COMMANDS=\
	diags \
	internal

INTERNALS=\
	nothing

M4INTERNALS=\
	list

PROFILE_D=\
	pscheduler.csh \
	pscheduler.sh


ALLPROGRAMS=$(PROGRAMS) $(M4PROGRAMS)
ALLCOMMANDS=$(COMMANDS) $(M4COMMANDS)
ALLINTERNALS=$(INTERNALS) $(M4INTERNALS)

ALLM4=$(M4PROGRAMS) $(M4COMMANDS) $(M4INTERNALS)
ALLM4=$(ALLM4:%=%.m4)

ALL=$(ALLPROGRAMS) $(ALLCOMMANDS) $(ALLINTERNALS)


default:  build

%: %.m4
ifndef COMMANDSINSTALLED
	@echo No COMMANDSINSTALLED specified for build of $@
	@false
endif
ifndef CLASSESINSTALLED
	@echo No CLASSESINSTALLED specified for build of $@
	@false
endif
ifndef INTERNALSINSTALLED
	@echo No INTERNALSSINSTALLED specified for build of $@
	@false
endif
ifndef TOOLCONFIGDIR
	@echo No TOOLCONFIGDIR specified for build of $@
	@false
endif
	m4 \
		-D__COMMANDS__=$(COMMANDSINSTALLED) \
		-D__CLASSES__=$(CLASSESINSTALLED) \
		-D__INTERNALS__=$(INTERNALSINSTALLED) \
		-D__TOOLCONFIGDIR__=$(TOOLCONFIGDIR) \
		$< > $@


build: $(ALL)
TO_CLEAN += $(M4PROGRAMS) $(M4COMMANDS) $(M4INERNALS)


install: $(ALL)
ifndef BINDIR
	@echo No BINDIR specified for installation
	@false
endif
ifndef COMMANDSDIR
	@echo No COMMANDSDIR specified for installation
	@false
endif
ifndef INTERNALSDIR
	@echo No INTERNALSDIR specified for installation
	@false
endif
ifndef PROFILEDDIR
	@echo No PROFILEDDIR specified for installation
	@false
endif
	mkdir -p $(BINDIR)
	install -m 555 $(ALLPROGRAMS) $(BINDIR)
	mkdir -p $(COMMANDSDIR)
	install -m 555 $(ALLCOMMANDS) $(COMMANDSDIR)
	mkdir -p $(INTERNALSDIR)
	install -m 555 $(ALLINTERNALS) $(INTERNALSDIR)
	mkdir -p $(PROFILEDDIR)
	install -m 444 $(PROFILE_D) $(PROFILEDDIR)


clean:
	rm -rf $(TO_CLEAN) *~
