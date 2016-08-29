#
# Makefile for pScheduler full bundle
#

# This makefile auto-generates a spec based on the build list and then
# uses Makefile-RPM to build it the usual way.

# TODO: This bundle doesn't fix the need to have select
# repos-preinstalled into YUM.  Should maybe write a package that does
# that.

NAME=pscheduler-bundle-full

RPM_MAKEFILE=Makefile-RPM

default: build

SPEC=$(NAME).spec
$(SPEC): $(SPEC)-top $(SPEC)-bottom
	cat $(SPEC)-top > $@
	../scripts/build-order \
		| egrep -e '^pscheduler-' \
		| egrep -ve '^pscheduler-bundle-' \
		| sed -e 's/^/Requires: /g' \
		>> $@
	cat $(SPEC)-bottom >> $@
TO_CLEAN += $(SPEC)


# These add compatibility with the generic RPM makefile template's
# targets.

clean c: $(SPEC)
	$(MAKE) -f $(RPM_MAKEFILE) $@
	rm -rf $(TO_CLEAN) *~

build b install i rpmdump r cb cbr cbi srpm: $(SPEC)
	$(MAKE) -f $(RPM_MAKEFILE) $@

cbic cbrc: $(SPEC)
	$(MAKE) -f $(RPM_MAKEFILE) $@
	$(MAKE) clean
