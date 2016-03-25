#
# Makefile for pScheduler Programs
#
# The following variables must be provided externally:
#
#   BINDIR - Location for installed programs
#   INITDDIR - Location for installed init scripts (/etc/rc.d/init.d)
#

# TODO: Should probably generate the init.d files since they're all
# the same.

PROGRAMS=\
	pscheduler-api-server \
	pscheduler-archiver \
	pscheduler-runner \
	pscheduler-ticker \
	pscheduler-scheduler \


PROGRAMS_NOINIT=\
	pscheduler-monitor \

PROGRAMS_ALL=$(PROGRAMS) $(PROGRAMS_NOINIT)

INITS=$(PROGRAMS:%=%-init.d)

default: build


build: $(PROGRAMS) $(PROGRAMS_NOINIT) $(INITS)
	@true



# TODO: This target needs to have a SYSCONFDIR passed in and fill in
# the right value in the scripts.  (See TODOs)

install: build
ifndef BINDIR
	@echo No BINDIR specified for installation
	@false
endif
ifndef INITDDIR
	@echo No INITDDIR specified for installation
	@false
endif
	mkdir -p $(BINDIR)
	cp -f $(PROGRAMS_ALL) $(BINDIR)
	chmod 555 $(PROGRAMS:%=$(BINDIR)/%)
	mkdir -p $(INITDDIR)
	@for SCRIPT in $(PROGRAMS) ; \
	do \
		echo "Installing init.d for $${SCRIPT}" ; \
		cp -f $${SCRIPT}-init.d $(INITDDIR)/$${SCRIPT} ; \
		chmod 555 $(INITDDIR)/$${SCRIPT} ; \
	done




TODO=TODO:
todo:
	@fgrep '$(TODO)' $(SUPER) $(UNPRIV) Makefile \
	| sed -e 's/:.*$(TODO)\s*/~/' \
	| awk -F '~' 'BEGIN { FN="" } $$1 != FN { print "\n" $$1 ":"; FN=$$1 } { print "    ", $$2 }'


clean:
	rm -rf $(TO_CLEAN) *~
