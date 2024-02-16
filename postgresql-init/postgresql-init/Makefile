#
# Makefile for postgresql-init
#

PROGRAMS := \
	initialize-postgresql \
	upgrade-postgresql

default: build


%: %.raw
ifndef PG_DATA_DIR
	@echo No PG_DATA_DIR specified for installation
	@false
endif
ifndef PG_GROUP
	@echo No PG_GROUP specified for installation
	@false
endif
ifndef PG_INITDB
	@echo No PG_INITDB specified for installation
	@false
endif
ifndef PG_LIB
	@echo No PG_LIB specified for installation
	@false
endif
ifndef PG_SERVICE
	@echo No PG_SERVICE specified for installation
	@false
endif
ifndef PG_USER
	@echo No PG_USER specified for installation
	@false
endif
ifndef PG_USER
	@echo No PG_USER specified for installation
	@false
endif
ifndef PG_VERSION_FILE
	@echo No PG_VERSION_FILE specified for installation
	@false
endif
ifndef USR
	@echo No USR specified for installation
	@false
endif
	sed \
	    -e "s|__PG_DATA_DIR__|$(PG_DATA_DIR)|g" \
	    -e "s|__PG_GROUP__|$(PG_GROUP)|g" \
	    -e "s|__PG_INITDB__|$(PG_INITDB)|g" \
	    -e "s|__PG_LIB__|$(PG_LIB)|g" \
	    -e "s|__PG_SERVICE__|$(PG_SERVICE)|g" \
	    -e "s|__PG_VERSION_FILE__|$(PG_VERSION_FILE)|g" \
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
