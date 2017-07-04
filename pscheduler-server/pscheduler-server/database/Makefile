#
# Makefile for Database
#
# The following variables must be provided externally:
#
#   DATADIR - Location for installed SQL files (/usr/share/...)
#

DBNAME=pscheduler

FILES_SUPERUSER=\
	database \
	external_program \
	http_ops \
	json_validate

FILES=\
	preamble \
	utilities \
	table_version \
	\
	configurables \
	control \
	http_queue \
	scheduling_class \
	test \
	tool \
	archive_default \
	archiver \
	task \
	run_state \
	run \
	run_latest \
	archiving \
	schedule \
	boot \
	ticker \
	\
	postamble


FILES_TEARDOWN=\
	database-drop


SUPER=$(FILES_SUPERUSER:%=%.sql)
BUILD_SUPER_SQL=database-build-super.sql

UNPRIV=$(FILES:%=%.sql)
BUILD_SQL=database-build.sql

TEARDOWN=$(FILES_TEARDOWN:%=%.sql)
TEARDOWN_SQL=database-teardown.sql

SQL=$(BUILD_SUPER_SQL) $(BUILD_SQL) $(TEARDOWN_SQL)

INTERNALS=\
	db-update \
	reset \
	warmboot


%: %.raw
ifndef DATABASE
	@echo No DATABASE specified for build
	@false
endif
ifndef DATADIR
	@echo No DATADIR specified for build
	@false
endif
ifndef PASSWORDFILE
	@echo No PASSWORDFILE specified for build
	@false
endif
ifndef ROLE
	@echo No ROLE specified for build
	@false
endif
	sed \
		-e 's|__DATABASE__|$(DATABASE)|g' \
		-e 's|__DATADIR__|$(DATADIR)|g' \
		-e 's|__PASSWORDFILE__|$(PASSWORDFILE)|g' \
		-e 's|__ROLE__|$(ROLE)|g' \
		< $^ > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi
RAW_BUILT := $(shell find . -name "*.raw" | sed -e 's/\.raw$$//')
TO_CLEAN += $(RAW_BUILT)


default: build


build: check $(SQL) $(INTERNALS)


$(BUILD_SUPER_SQL): $(SUPER)
	cat $^ > $@
TO_CLEAN += $(BUILD_SUPER_SQL)


$(BUILD_SQL): $(UNPRIV)
	cat $^ > $@
TO_CLEAN += $(BUILD_SQL)


$(TEARDOWN_SQL): $(TEARDOWN)
	cat $^ > $@
TO_CLEAN += $(TEARDOWN_SQL)


# Note:  This must stay in this order so a test run will build and tear down the database.
GENERATED_SQL=$(BUILD_SUPER_SQL) $(BUILD_SQL) $(TEARDOWN_SQL)



#
# Test finished files for syntactical correctness if CHECK_SYNTAX is
# defined.
#

ifdef CHECK_SYNTAX

CHECK_PREFIX := $(shell echo build$$$$)
FULL_CHECK_SQL=check-full.sql
CHECK_DIR=./syntax-check

$(FULL_CHECK_SQL): $(GENERATED_SQL)
	cat $(GENERATED_SQL) > $@
TO_CLEAN += $(FULL_CHECK_SQL)

$(CHECK_DIR):
	mkdir -p $@
	cp Makefile *.sql *.raw $@
	$(MAKE) -C $@ clean
	$(MAKE) -C $@ DATABASE=$(CHECK_PREFIX) DATADIR=/dev/null ROLE=$(CHECK_PREFIX) PASSWORDFILE=/dev/null $(FULL_CHECK_SQL)
TO_CLEAN += $(CHECK_DIR)

DB_ERROR=.db_error

check: $(CHECK_DIR)
ifeq ($(shell id -u),0)
	@postgresql-load $(CHECK_DIR)/$(FULL_CHECK_SQL) || touch $(DB_ERROR)
	@echo "DROP DATABASE IF EXISTS $(CHECK_PREFIX);" | postgresql-load
	@[ -e $(DB_ERROR) ] && echo "Database syntax check failed." || true
	@[ ! -e $(DB_ERROR) ]
	@echo Database syntax OK
else
	@echo
	@echo "WARNING: Not running as root; not checking database syntax."
	@echo
endif
TO_CLEAN += $(DB_ERROR)

else

check:
	@echo Source syntax checking is not enabled.  Skipping.

endif



#
# Installation
#

install:
ifndef DATADIR
	@echo No DATADIR specified for installation
	@false
endif
ifndef INTERNALSDIR
	@echo No INTERNALSDIRDIR specified for installation
	@false
endif
	mkdir -p $(DATADIR)
	install -m 440 $(SQL) $(DATADIR)
	mkdir -p $(INTERNALSDIR)
	install -m 550 $(INTERNALS) $(INTERNALSDIR)


clean:
	rm -rf $(TO_CLEAN) *~
