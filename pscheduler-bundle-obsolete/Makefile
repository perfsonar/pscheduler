#
# Makefile for pScheduler obsolete bundle
#

# This makefile auto-generates a spec based on the build list and then
# uses Makefile-package to build it the usual way.

# TODO: This bundle doesn't fix the need to have select
# repos-preinstalled into YUM.  Should maybe write a package that does
# that.

NAME=pscheduler-bundle-obsolete

PACKAGE_MAKEFILE=Makefile-package

default: build

SPEC=./rpm/$(NAME).spec
$(SPEC): $(SPEC)-top $(SPEC)-bottom
	cat $(SPEC)-top > $@
	../scripts/build-order --bundle obsolete \
		| egrep -e '^pscheduler-' \
		| egrep -ve '^pscheduler-bundle-' \
		| sed -e 's/^/Requires: /g' \
		>> $@
	cat $(SPEC)-bottom >> $@
TO_CLEAN += $(SPEC)

# These add compatibility with the generic package makefile template's
# targets.

clean c:
	$(MAKE) $(SPEC)
	$(MAKE) -f $(PACKAGE_MAKEFILE) $@
	rm -rf $(TO_CLEAN) *~

build b install i rpmdump d r cb cbd cbr cbi srpm:
	$(MAKE) $(SPEC)
	$(MAKE) -f $(PACKAGE_MAKEFILE) $@

cbic cbdc cbrc:
	$(MAKE) $(SPEC)
	$(MAKE) -f $(PACKAGE_MAKEFILE) $@
	$(MAKE) clean


# This is to keep the global uninstall target happy.
uninstall:
	@echo Nothing to do here.
