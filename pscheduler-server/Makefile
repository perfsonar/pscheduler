#
# Makefile for pscheduler-server
#

# This has to be built differently on different flavors of Debian and
# Ubuntu.  Set that up.

OS_PACKAGING := $(shell unibuild macros PACKAGING)


ifeq ($(OS_PACKAGING),deb)

  default: build

  ifndef STAGE2
    %:
	$(MAKE) -C ./pscheduler-server/unibuild-packaging/$(OS_PACKAGING)
	$(MAKE) STAGE2=1 $@
  else
    include unibuild/unibuild.make
  endif  # STAGE2


else  #deb

  include unibuild/unibuild.make

endif  # deb
