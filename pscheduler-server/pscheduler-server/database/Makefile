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
	http_ops

FILES=\
	preamble \
	utilities \
	table_version \
	\
	configurables \
	http_queue \
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
	reset \
	warmboot

%: %.m4
ifndef DATABASE
	@echo No DATABASE specified for build
	@false
endif
ifndef ROLE
	@echo No ROLE specified for build
	@false
endif
	m4 \
	-D__DATABASE__=$(DATABASE) \
	-D__ROLE__=$(ROLE) \
	< $^ > $@
TO_CLEAN += $(INTERNALS)


default: build


build: $(SQL) $(INTERNALS)


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
