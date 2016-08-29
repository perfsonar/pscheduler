#
# Makefile for pScheduler Programs
#
# The following variables must be provided externally:
#
#   COMMANDDIR - Location for installed programs
#   DAEMONDIR - Where daemon programs should be installed
#   DSNFILE - Location of DSN file for database logins
#   INITDDIR - Location for installed init scripts (/etc/rc.d/init.d)
#   PGPASSFILE - Path to PostgreSQL password file
#   PGUSER - Name of pScheduler PostgreSQL account
#   PSUSER - Name of pScheduler user account
#   VAR - Location of /var directory
#

DAEMONS=\
	archiver \
	runner \
	ticker \
	scheduler \


COMMANDS=\
	debug \
	monitor

INITS=$(DAEMONS:%=init.d-%)

default: build


archiver: archiver.m4
ifndef ARCHIVERDEFAULTDIR
	@echo No ARCHIVERDEFAULTDIR specified for build
	@false
endif
	m4 \
		-D__DEFAULT_DIR__=$(ARCHIVERDEFAULTDIR) \
		< $< > $@
TO_CLEAN += archiver


monitor: monitor.m4
ifndef PGPASSFILE
	@echo No PGPASSFILE specified for build
	@false
endif
ifndef PGUSER
	@echo No PGUSER specified for build
	@false
endif
ifndef PGDATABASE
	@echo No PGDATABASE specified for build
	@false
endif
	m4 \
		-D__PGPASSFILE__=$(PGPASSFILE) \
		-D__PGUSER__=$(PGUSER) \
		-D__PGDATABASE__=$(PGDATABASE) \
		< $< > $@
TO_CLEAN += monitor

$(INITS): init.d-template.m4
ifndef DAEMONDIR
	@echo No DAEMONDIR specified for build
	@false
endif
ifndef DSNFILE
	@echo No DSNFILE specified for build
	@false
endif
ifndef PSUSER
	@echo No PSUSER specified for build
	@false
endif
ifndef VAR
	@echo No VAR specified for build
	@false
endif
	m4 \
		-D__DAEMONDIR__=$(DAEMONDIR) \
		-D__DSN__=$(DSNFILE) \
		-D__PROG__=$(@:init.d-%=%) \
		-D__PSUSER__=$(PSUSER) \
		-D__VAR__=$(VAR) \
		< $< > $@
TO_CLEAN += $(INITS)


build: $(DAEMONS) $(INITS) $(COMMANDS)
	@true



# TODO: This target needs to have a SYSCONFDIR passed in and fill in
# the right value in the scripts.  (See TODOs)

install: build
ifndef COMMANDDIR
	@echo No COMMANDDIR specified for installation
	@false
endif
ifndef DAEMONDIR
	@echo No DAEMONDIR specified for installation
	@false
endif
ifndef INITDDIR
	@echo No INITDDIR specified for installation
	@false
endif
	mkdir -p $(COMMANDDIR)
	cp -f $(COMMANDS) $(COMMANDDIR)
	chmod 555 $(COMMANDS:%=$(COMMANDDIR)/%)
	mkdir -p $(DAEMONDIR)
	cp -f $(DAEMONS) $(DAEMONDIR)
	chmod 555 $(DAEMONS:%=$(DAEMONDIR)/%)
	mkdir -p $(INITDDIR)
	@for SCRIPT in $(DAEMONS) ; \
	do \
		echo "Installing init.d for $${SCRIPT}" ; \
		cp -f init.d-$${SCRIPT} $(INITDDIR)/pscheduler-$${SCRIPT} ; \
		chmod 555 $(INITDDIR)/pscheduler-$${SCRIPT} ; \
	done


clean:
	rm -rf $(TO_CLEAN) *~
