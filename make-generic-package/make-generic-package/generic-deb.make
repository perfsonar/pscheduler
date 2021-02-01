#
# Generic Makefile for Debian packagess
#

#
# NO USER-SERVICEABLE PARTS BELOW THIS LINE
#

default: build


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



build: $(BUILD_UNPACK_DIR) $(BUILD_PATCHES_DIR) $(BUILD_PATCHES) $(PRODUCTS_DIR)
	cd $(BUILD_UNPACK_DIR) \
		&& dpkg-buildpackage --build=all --root-command=fakeroot --no-sign
	mv $(BUILD_DIR)/$(NAME)_$(VERSION)-* $(PRODUCTS_DIR)



install: build
	@find $(BUILD_DIR) -name "*.deb" \
		| xargs sudo dpkg -i


uninstall: build
	@find $(BUILD_DIR) -name "*.deb" \
		| sed -e 's|^.*/||; s/_.*$$//' \
		| xargs sudo dpkg -r

dump:
	@if [ ! -d "$(PRODUCTS_DIR)" ] ; \
	then \
		printf "\nPackage is not built.\n\n" ; \
		false ; \
	fi
	@find $(PRODUCTS_DIR) -name "*.deb" \
	| ( \
	    while read DEB ; \
	    do \
	        echo "$$DEB" | sed -e 's|^$(BUILD_DIR)/||' | xargs -n 1 printf "\n%s:\n" ; \
	        dpkg --contents "$$DEB" ; \
	        echo ; \
	    done)

