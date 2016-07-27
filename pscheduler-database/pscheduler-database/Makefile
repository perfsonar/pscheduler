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
	test \
	tool \
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



install: $(SQL)
ifndef DATADIR
	@echo No DATADIR specified for installation
	@false
endif
	mkdir -p $(DATADIR)
	# These only need to be readable by the owner or trusted associates.
	install -m 440 $^ $(DATADIR)


clean:
	rm -rf $(TO_CLEAN) *~
