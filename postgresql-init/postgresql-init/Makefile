#
# Makefile for postgresql-init
#

PROGRAMS := \
	upgrade-postgresql

default: build


%: %.raw
ifndef PG_LIB
	@echo No PG_LIB specified for installation
	@false
endif
ifndef PG_USER
	@echo No PG_USER specified for installation
	@false
endif
ifndef USR
	@echo No USR specified for installation
	@false
endif
	sed \
	    -e "s|__PG_LIB__|$(PG_LIB)|g" \
	    -e "s|__PG_USER__|$(PG_USER)|g" \
	    -e "s|__USR__|$(USR)|g" \
	$< > $@

build: $(PROGRAMS)
TO_CLEAN += $(PROGRAMS)


$(DESTDIR):
	mkdir -p $@


$(DESTDIR)/%: %
	install -m 555 $< $@

INSTALLED := $(PROGRAMS:%=$(DESTDIR)/%)
$(INSTALLED): $(DESTDIR)


install: $(INSTALLED)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif


clean:
	rm -f $(TO_CLEAN) *~
