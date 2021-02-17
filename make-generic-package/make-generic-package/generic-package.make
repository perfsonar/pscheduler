#
# Include a package-building Makefile depending on the system's
# packaging model.
#

# generic-*.make will define this target.

default: build


# This is used to make sure the RPM and Debian templates aren't
# included directly.
GENERIC_PACKAGE_MAKE=1

# Figure out what kind of packages are used by this system

DISTRO_FAMILY := $(shell lsb_release --id --short)

ifeq "$(DISTRO_FAMILY)" ""
$(error "Unable to determine Linux distribution.  (Is lsb_releases installed?)")
endif

ifneq "$(filter AlmaLinux CentOS Fedora,$(DISTRO_FAMILY))" ""
PACKAGE_FORMAT := rpm
endif

ifneq "$(filter Debian Ubuntu,$(DISTRO_FAMILY))" ""
PACKAGE_FORMAT := deb
endif

ifeq "$(PACKAGE_FORMAT)" ""
$(error "Don't know how to package for $(DISTRO_FAMILY)")
endif


# Standard directories and files


TOP := $(CURDIR)

# Where the build happens
BUILD_DIR := ./BUILD
$(BUILD_DIR)::
	mkdir -p $@
TO_BUILD += $(BUILD_DIR)
TO_CLEAN += $(BUILD_DIR)

# Where the finished products go
PRODUCTS_DIR := ./PRODUCTS
$(PRODUCTS_DIR):
	mkdir -p $@
TO_BUILD += $(PRODUCTS_DIR)
TO_CLEAN += $(PRODUCTS_DIR)

# Build log
BUILD_LOG := $(TOP)/LOG
TO_CLEAN += $(BUILD_LOG)

# A place to create temporary files
TMP_DIR := $(TOP)/TMP
$(TMP_DIR):
	mkdir -p $@
TO_CLEAN += $(TMP_DIR)



# Include the right version for this package format

ifdef BUILD_PATH
include $(BUILD_PATH)/generic-$(PACKAGE_FORMAT).make
else
include make/generic-$(PACKAGE_FORMAT).make
endif



# Standard targets

clean::
	rm -rf $(TO_CLEAN)
	find . -name '*~' | xargs rm -rf

ifdef AUTO_TARBALL
clean::
	find . -depth -name Makefile \
	    -exec /bin/sh -c \
	    '[ "{}" != "./Makefile" ] && make -C `dirname {}` clean' \;
endif



# Convenient shorthands for targets in the templates included above.

b: build
c: clean
i: install
d: dump

cb: c b
cbd: c b d
cbi: c b i

# CBI with forced clean afterward
cbic: cbi
	@$(MAKE) clean

# CBR with forced clean afterward
cbdc: cbd
	@$(MAKE) clean


# These are deprecated holdovers from the RPM-only days

r:
	@printf "\n\nThe '$@' target is deprecated, use 'd' instead.  Continuing shortly.\n\n"
	@sleep 3
	@$(MAKE) d

cbr:
	@printf "\n\nThe '$@' target is deprecated, use 'cbd' instead.  Continuing shortly.\n\n"
	@sleep 3
	@$(MAKE) cbd

rpmdump:
	@printf "\n\nThe '$@' target is deprecated, use 'dump' instead.  Continuing shortly.\n\n"
	@sleep 3
	@$(MAKE) dump

cbrc:
	@printf "\n\nThe '$@' target is deprecated, use 'cbdc' instead.  Continuing shortly.\n\n"
	@sleep 3
	@$(MAKE) cbdc
