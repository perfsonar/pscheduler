#
# Makefile for pScheduler Programs
#
# The following variables must be provided externally:
#
#   COMMANDDIR - Location for installed programs
#   DAEMONDIR - Where daemon programs should be installed
#   DSNFILE - Location of DSN file for database logins
#   UNITDIR - Location for installed systemd units
#   PGPASSFILE - Path to PostgreSQL password file
#   PGSERVICE - Name of the PostgreSQL systemd service
#   PGUSER - Name of pScheduler PostgreSQL account
#   PSUSER - Name of pScheduler user account
#   RUNDIR - Location of run directory (nominally /run)
#   VAR - Location of /var directory
#

DAEMONS=\
	archiver \
	runner \
	ticker \
	scheduler \


COMMANDS=\
	debug \
	pause \
	resume

INTERNALS=\
	threads


UNITS=$(DAEMONS:%=service-%)

CONFIGS=$(DAEMONS:%=%.conf)

default: build


archiver: archiver.raw
ifndef ARCHIVERDEFAULTDIR
	@echo No ARCHIVERDEFAULTDIR specified for build
	@false
endif
	sed \
		-e 's|__DEFAULT_DIR__|$(ARCHIVERDEFAULTDIR)|g' \
		< $< > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi
TO_CLEAN += archiver


debug: debug.raw
ifndef PSUSER
	@echo No PSUSER specified for build
	@false
endif
	sed \
		-e 's|__PSUSER__|$(PSUSER)|g' \
		-e 's|__RUNDIR__|$(RUNDIR)|g' \
		< $< > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi
TO_CLEAN += debug


monitor: monitor.raw
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
	sed \
		-e 's|__PGPASSFILE__|$(PGPASSFILE)|g' \
		-e 's|__PGUSER__|$(PGUSER)|g' \
		-e 's|__PGDATABASE__|$(PGDATABASE)|g' \
		< $< > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi
TO_CLEAN += monitor


pause: pause.raw
ifndef DSNFILE
	@echo No DSNFILE specified for build
	@false
endif
	sed \
		-e 's|__DSNFILE__|$(DSNFILE)|g' \
		< $< > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi
TO_CLEAN += pause


resume: resume.raw
ifndef DSNFILE
	@echo No DSNFILE specified for build
	@false
endif
	sed \
		-e 's|__DSNFILE__|$(DSNFILE)|g' \
		< $< > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi
TO_CLEAN += resume



$(UNITS): service-template.raw
ifndef CONFIGDIR
	@echo No CONFIGDIR specified for build
	@false
endif
ifndef DAEMONDIR
	@echo No DAEMONDIR specified for build
	@false
endif
ifndef DSNFILE
	@echo No DSNFILE specified for build
	@false
endif
ifndef LOGDIR
	@echo No LOGDIR specified for build
	@false
endif
ifndef PSUSER
	@echo No PSUSER specified for build
	@false
endif
ifndef PGSERVICE
	@echo No PGSERVICE specified for build
	@false
endif
ifndef RUNDIR
	@echo No RUNDIR specified for build
	@false
endif
ifndef VAR
	@echo No VAR specified for build
	@false
endif
	sed \
		-e 's|__CONFIGDIR__|$(CONFIGDIR)|g' \
		-e 's|__DAEMONDIR__|$(DAEMONDIR)|g' \
		-e 's|__DSN__|$(DSNFILE)|g' \
		-e 's|__PROG__|$(@:service-%=%)|g' \
		-e 's|__PSUSER__|$(PSUSER)|g' \
		-e 's|__RUNDIR__|$(RUNDIR)|g' \
		-e 's|__VAR__|$(VAR)|g' \
		-e 's|__LOGDIR__|$(LOGDIR)|g' \
		-e 's|__PGSERVICE__|$(PGSERVICE)|g' \
		< $< > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi
TO_CLEAN += $(UNITS)


$(CONFIGS): config-template.raw
	sed \
		-e 's|__PROG__|$(@:%.conf=%)|g' \
		< $< > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi
TO_CLEAN += $(CONFIGS)


build: $(DAEMONS) $(UNITS) $(CONFIGS) $(COMMANDS) $(INTERNALS)
	@true



# TODO: This target needs to have a SYSCONFDIR passed in and fill in
# the right value in the scripts.  (See TODOs)

install: build
ifndef CONFIGDIR
	@echo No CONFIGDIR specified for installation
	@false
endif
ifndef COMMANDDIR
	@echo No COMMANDDIR specified for installation
	@false
endif
ifndef DAEMONDIR
	@echo No DAEMONDIR specified for installation
	@false
endif
ifndef UNITDIR
	@echo No UNITDIR specified for installation
	@false
endif
	mkdir -p $(CONFIGDIR)
	cp -f $(CONFIGS) $(CONFIGDIR)
	chmod 600 $(CONFIGS:%=$(CONFIGDIR)/%)
	mkdir -p $(COMMANDDIR)
	cp -f $(COMMANDS) $(COMMANDDIR)
	chmod 555 $(COMMANDS:%=$(COMMANDDIR)/%)
	mkdir -p $(DAEMONDIR)
	cp -f $(DAEMONS) $(DAEMONDIR)
	chmod 555 $(DAEMONS:%=$(DAEMONDIR)/%)
	cp -f $(INTERNALS) $(INTERNALSDIR)
	chmod 555 $(INTERNALS:%=$(INTERNALSDIR)/%)
	mkdir -p $(UNITDIR)
	@for SCRIPT in $(DAEMONS) ; \
	do \
		echo "Installing service for $${SCRIPT}" ; \
		cp -f service-$${SCRIPT} $(UNITDIR)/pscheduler-$${SCRIPT}.service ; \
		chmod 444 $(UNITDIR)/pscheduler-$${SCRIPT}.service ; \
	done


clean:
	rm -rf $(TO_CLEAN) *~
