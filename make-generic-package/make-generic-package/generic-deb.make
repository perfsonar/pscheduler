#
# Generic Makefile for Debian packagess
#
# To use this file, create a Makefile containing the following:
#
#     inclulde make/generic-deb.make
#
# Targets (Shortcuts in Parentheses):
#
#     build (b) - Build the RPM.  This is the default target.
#     clean (c) - Remove build by-products
#     install (i) - Install the RPM forcibly.  Must be run as a user
#                   that can do this.
#     rpmdump (r) - Dump contents of built RPMs.
#
# Other useful shortcut targets:
#
#     cb - Clean and build
#     cbr - Clean, build and rpmdump
#     cbi - Clean, build and install
#     cbic - Clean, build and install and forced re-clean
#     cbrc - Clean, build, rpmdump and forced re-clean
#
#
# To construct a tarball of your sources automatically:
#
#   - Name a subdirectory with the name of the product (e.g, foomatic)
#   - Specify a tarball in the source (e.g., Source0: foomatic-1.3.tar.gz)
#   - Set AUTO_TARBALL=1 in your makefile
#
#   NOTE:  The version number in the spec may not contain hyphens.
#

#
# NO USER-SERVICEABLE PARTS BELOW THIS LINE
#

default: build


BUILD_DIR := ./BUILD
TO_CLEAN += $(BUILD_DIR)

#
# Get basic package information
#

DEB_DIR := $(shell find . -type d -name "debian" | egrep -ve '^$(BUILD_DIR)')
ifeq "$(DEB_DIR)" ""
$(error "Unable to find debian directory.")
endif
ifneq "$(words $(DEB_DIR))" "1"
$(error "Found more than one debian directory.  There can be only one.")
endif

CONTROL := $(DEB_DIR)/control
NAME := $(shell awk '-F: ' '$$1 == "Package" { print $$2 }' $(CONTROL))
ifeq "$(CONTROL)" ""
$(error "Unable to find package name in $(CONTROL).")
endif

CHANGELOG := $(DEB_DIR)/changelog
VERSION := $(shell awk -v 'NAME=$(NAME)' '$$1 == NAME { print $$2 ; exit }' '$(CHANGELOG)' \
	| sed -e 's/^.\([^-]*\).*$$/\1/ ' )


#
# Build Directory and its Contents
#

BUILD_UNPACK_DIR := $(BUILD_DIR)/$(NAME)-$(VERSION)
$(BUILD_UNPACK_DIR):
	mkdir -p $@
	(cd '$(NAME)' && tar cf - .) | (cd '$(BUILD_UNPACK_DIR)' && tar xpf -)
BUILD_DEBIAN_DIR := $(BUILD_UNPACK_DIR)/debian

PATCHES_SERIES := $(DEB_DIR)/patches/series
PATCHES := $(shell sed -e '/^\s*\#/d' '$(PATCHES_SERIES)')
BUILD_PATCHES_DIR := $(BUILD_DEBIAN_DIR)/patches
BUILD_PATCHES := $(PATCHES:%=$(BUILD_PATCHES_DIR)/%)

$(BUILD_PATCHES_DIR):
	mkdir -p $@

$(BUILD_PATCHES_DIR)/%: ./%
	cp -f $< $@


foo:
	@echo $(BUILD_PATCHES)



build: \
	$(BUILD_UNPACK_DIR) \
	$(BUILD_PATCHES_DIR) \
	$(BUILD_PATCHES)
#cd $(BUILD_UNPACK_DIR) && apt build-dep '$(NAME)'
	cd $(BUILD_UNPACK_DIR) && dpkg-buildpackage -rfakeroot -b -uc -us

dump:
	@if [ ! -d "$(BUILD_DIR)" ] ; \
	then \
		printf "\nPackage is not built.\n\n" ; \
		false ; \
	fi
	@find $(BUILD_DIR) -name "*.deb" \
	| ( \
	    while read DEB ; \
	    do \
	        echo "$$DEB" | sed -e 's|^$(BUILD_DIR)/||' | xargs -n 1 printf "\n%s:\n" ; \
	        dpkg --contents "$$DEB" ; \
	        echo ; \
	    done)


clean::
	rm -rf $(TO_CLEAN)
	find . -name '*~' | xargs rm -rf
