#
# Make-generic-package Makefile, Stage 1
#

default: build

include ./make-generic-package/generic-common.make

ifeq "$(PACKAGE_FORMAT)" "rpm"

%:
	which spectool > /dev/null 2>&1 || yum -y install spectool
	which rpmbuild > /dev/null 2>&1 || yum -y install rpm-build
	$(MAKE) -f Makefile-stage2 $@

else

%:
	$(MAKE) -f Makefile-stage2 $@

endif
