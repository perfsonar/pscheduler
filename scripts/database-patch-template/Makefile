#
# Makefile for pScheduler database Patch
#

# Configure the following to taste:

# Patch name
NAME=example-patch

# Names of SQL files to include as part of the patch
SQL_FILES=example

# Database name
DATABASE=pscheduler

# Database role
ROLE=pscheduler


# No user-serviceable parts below this line.

SQLS=$(SQL_FILES:%=%.sql)

default:
	@echo "Targets are 'install', 'revert', 'tar' and 'clean'."


PATCH=patch.sql
$(PATCH): $(SQLS)
	rm -f $@
	echo '\c $(DATABASE)' >> $@
	echo 'SET ROLE $(ROLE);' >> $@
	cat $(SQLS) >> $@
TO_CLEAN += $(PATCH)

build: $(PATCH)


install: $(PATCH)
	@[ "$$(id -un)" = "root" ] \
	    || (echo "This must be done as root." && false)
	postgresql-load $<


revert:
	pscheduler internal db-update


TAR=$(NAME).tar.gz
TAR_BUILD=./tarball
TAR_DIR=$(TAR_BUILD)/$(NAME)
TAR_PARTS=Makefile $(SQLS)
$(TAR):
	mkdir -p $(TAR_DIR)
	cp $(TAR_PARTS) $(TAR_DIR)
	(cd $(TAR_BUILD) && tar czf - *) > $@
	rm -rf $(TAR_BUILD)
TO_CLEAN += $(TAR) $(TAR_BUILD)

tar: $(TAR)


clean:
	rm -rf $(TO_CLEAN)
	find . -name "*~" -print0 | xargs -0 rm -rf
