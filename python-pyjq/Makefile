#
# Makefile for python-pyjq
#

# This has to be built differently on different flavors of Debian and
# Ubuntu.  Set that up.

ifdef STAGE2

include unibuild/unibuild.make

else  # STAGE2

default: build

OS_PACKAGING := $(shell unibuild macros PACKAGING)

ifeq ($(OS_PACKAGING),deb)
build clean::
	$(MAKE) -C ./unibuild-packaging/$(OS_PACKAGING) $@
	$(MAKE) STAGE2=1 $@

%::
	$(MAKE) STAGE2=1 $@

endif

endif  # STAGE2
