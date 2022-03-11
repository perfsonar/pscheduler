#
# Makefile for pScheduler extras bundle
#

# This makefile auto-generates RPM spec and Debian control files based
# on the build list and then uses Makefile-package to build it the
# usual way.

# TODO: This bundle doesn't fix the need to have select
# repos-preinstalled into YUM.  Should maybe write a package that does
# that.

BUNDLE=snmp
NAME=pscheduler-bundle-$(BUNDLE)

PACKAGE_MAKEFILE=Makefile-package

default: build


UNIBUILD_ORDER := unibuild order \
	--file ../unibuild-order \
	--buildable \
	--bundle "$(BUNDLE)"

SPEC=./unibuild-packaging/rpm/$(NAME).spec
$(SPEC):
	cat $(SPEC)-top > $@
	$(UNIBUILD_ORDER) \
		| egrep -e '^pscheduler-' \
		| egrep -ve '^pscheduler-bundle-' \
		| sed -e 's/^/Requires: /g' \
		>> $@
	cat $(SPEC)-bottom >> $@
TO_BUILD += $(SPEC)

CONTROL=./unibuild-packaging/deb/control
$(CONTROL):
	cat $(CONTROL)-top > $@
	$(UNIBUILD_ORDER) \
		| egrep -e '^pscheduler-' \
		| egrep -ve '^pscheduler-bundle-' \
		| sed -e 's/^/ /g; $$ ! s/$$/,/g' \
		>> $@
	cat $(CONTROL)-bottom >> $@
TO_BUILD += $(CONTROL)


# These add compatibility with the generic package makefile template's
# targets.

TO_CLEAN += $(TO_BUILD)

clean c:
	$(MAKE) $(TO_BUILD)
	$(MAKE) -f $(PACKAGE_MAKEFILE) $@
	rm -rf $(TO_CLEAN) *~

build b install i rpmdump d r cb cbd cbr cbi srpm:
	$(MAKE) $(TO_BUILD)
	$(MAKE) -f $(PACKAGE_MAKEFILE) $@

cbic cbdc cbrc:
	$(MAKE) $(TO_BUILD)
	$(MAKE) -f $(PACKAGE_MAKEFILE) $@
	$(MAKE) clean


# This is to keep the global uninstall target happy.
uninstall:
	@echo Nothing to do here.
