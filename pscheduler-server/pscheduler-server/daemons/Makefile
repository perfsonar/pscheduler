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


INITS=$(DAEMONS:%=init.d-%)

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

$(INITS): init.d-template.raw
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
ifndef VAR
	@echo No VAR specified for build
	@false
endif
	sed \
		-e 's|__DAEMONDIR__|$(DAEMONDIR)|g' \
		-e 's|__DSN__|$(DSNFILE)|g' \
		-e 's|__PROG__|$(@:init.d-%=%)|g' \
		-e 's|__PSUSER__|$(PSUSER)|g' \
		-e 's|__VAR__|$(VAR)|g' \
		-e 's|__LOGDIR__|$(LOGDIR)|g' \
		< $< > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi
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
