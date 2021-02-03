#
# Make-generic-package Makefile
#

# TODO: When you run the default target (i.e., just 'make'), it builds
# twice.  Not really a problem, just an annoyance.

default: build


# Figure out what kind of packages are used by this system.  This is
# verbatim from generic-package.make

DISTRO_FAMILY := $(shell lsb_release --id --short)

ifeq "$(DISTRO_FAMILY)" ""
$(error "Unable to determine Linux distribution.  (Is lsb_releases installed?)")
endif

ifneq "$(filter CentOS Fedora,$(DISTRO_FAMILY))" ""
PACKAGE_FORMAT := rpm
endif

ifneq "$(filter Debian Ubuntu,$(DISTRO_FAMILY))" ""
PACKAGE_FORMAT := deb
endif

ifeq "$(PACKAGE_FORMAT)" ""
$(error "Don't know how to package for $(DISTRO_FAMILY)")
endif



ifeq "$(PACKAGE_FORMAT)" "rpm"

# TODO: Make sure this still works on CentOS.
prep:
	which spectool > /dev/null 2>&1 || sudo yum -y install spectool
	which rpmbuild > /dev/null 2>&1 || sudo yum -y install rpm-build

else

prep:
	@true

endif



ifndef STAGE2

# Stage 1: Do prep and launch the real thing.

%: prep
	$(MAKE) STAGE2=1 $@

else

# Stage 2: Build the package.

AUTO_TARBALL=1
BUILD_PATH=./make-generic-package

INC=$(BUILD_PATH)
# Eat a healthy dose of our own dog food
include $(BUILD_PATH)/generic-package.make

endif
