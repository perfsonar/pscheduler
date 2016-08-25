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
	external_program

FILES=\
	preamble \
	utilities \
	\
	configurables \
	scheduling_class \
	test \
	tool \
	archive_default \
	archiver \
	task \
	run_state \
	run \
	archiving \
	schedule \
	\
	boot \
	ticker \


FILES_TEARDOWN=\
	database-drop


# pScheduler internal commands
INTERNALS=\
	load-default-archives



SUPER=$(FILES_SUPERUSER:%=%.sql)
BUILD_SUPER_SQL=database-build-super.sql

UNPRIV=$(FILES:%=%.sql)
BUILD_SQL=database-build.sql

TEARDOWN=$(FILES_TEARDOWN:%=%.sql)
TEARDOWN_SQL=database-teardown.sql

SQL=$(BUILD_SUPER_SQL) $(BUILD_SQL) $(TEARDOWN_SQL)


default: build


build: $(SQL)


$(BUILD_SUPER_SQL): $(SUPER)
	cat $^ > $@
	chmod -w $@
TO_CLEAN += $(BUILD_SUPER_SQL)


$(BUILD_SQL): $(UNPRIV)
	cat $^ > $@
	chmod -w $@
TO_CLEAN += $(BUILD_SQL)


$(TEARDOWN_SQL): $(TEARDOWN)
	cat $^ > $@
	chmod -w $@
TO_CLEAN += $(TEARDOWN_SQL)


install: $(SQL) $(INTERNALS)
ifndef DATADIR
	@echo No DATADIR specified for installation
	@false
endif
ifndef INTERNALDIR
	@echo No INTERNALDIR specified for installation
	@false
endif
	mkdir -p $(DATADIR)
	install -m 440 $(SQL) $(DATADIR)
	mkdir -p $(INTERNALDIR)
	install -m 440 $(SQL) $(INTERNALDIR)


clean:
	rm -rf $(TO_CLEAN) *~
