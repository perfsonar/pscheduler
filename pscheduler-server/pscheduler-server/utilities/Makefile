#
# Makefile for pScheduler Programs
#
# See the .raw target for variables that must be provided externally.
#
#

COMMANDS=\
	backup \
	limit-diags \
	restore

default: build


%: %.raw
ifndef CONFIGDIR
	@echo CONFIGDIR not defined for $@
	false
endif
ifndef LIMITSFILE
	@echo LIMITSFILE not defined for $@
	false
endif
ifndef PGDATABASE
	@echo PGDATABASE not defined for $@
	false
endif
ifndef PGPASSFILE
	@echo PGPASSFILE not defined for $@
	false
endif
ifndef TMPDIR
	@echo TMPDIR not defined for $@
	false
endif
ifndef VERSION
	@echo VERSION not defined for $@
	false
endif
	sed \
		-e 's|__CONFIGDIR__|$(CONFIGDIR)|g' \
		-e 's|__LIMITSFILE__|$(LIMITSFILE)|g' \
		-e 's|__PGDATABASE__|$(PGDATABASE)|g' \
		-e 's|__PGPASSFILE__|$(PGPASSFILE)|g' \
		-e 's|__TMPDIR__|$(TMPDIR)|g' \
		-e 's|__VERSION__|$(VERSION)|g' \
		< $< > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi
TO_CLEAN += $(COMMANDS)





build: $(COMMANDS)
	@true



# TODO: This target needs to have a SYSCONFDIR passed in and fill in
# the right value in the scripts.  (See TODOs)

install: build
ifndef DESTDIR
	@echo DESTDIR not defined for $@
	false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(COMMANDS) $(DESTDIR)

clean:
	rm -rf $(TO_CLEAN) *~
