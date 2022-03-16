#
# Makefile for python-pyjq
#

# This has to be built differently on different flavors of Debian and
# Ubuntu.  Set that up.

OS_PACKAGING := $(shell unibuild macros PACKAGING)

ifeq ($(OS_PACKAGING),deb)
build clean::
	$(MAKE) -C ./unibuild-packaging/$(OS_PACKAGING) $@
endif


include unibuild/unibuild.make
