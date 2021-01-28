#
# Include a package-building Makefile depending on the system's
# packaging model.
#

# Figure out what kind of packages this system runs on

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



ifdef BUILD_PATH
include $(BUILD_PATH)/generic-$(PACKAGE_FORMAT).make
else
include make/generic-$(PACKAGE_FORMAT).make
endif
