#
# Generic Makefile for Debian packagess
#

#
# NO USER-SERVICEABLE PARTS BELOW THIS LINE
#

ifndef GENERIC_PACKAGE_MAKE
$(error "Include generic-package.make, not an environment-specific template.")
endif


# Basic package information

DEBIAN_DIR := $(shell find . -type d -name "debian" | egrep -ve '^$(BUILD_DIR)')
ifeq "$(DEBIAN_DIR)" ""
$(error "Unable to find debian directory.")
endif
ifneq "$(words $(DEBIAN_DIR))" "1"
$(error "Found more than one debian directory.  There can be only one.")
endif

CONTROL := $(DEBIAN_DIR)/control
NAME := $(shell awk '-F: ' '$$1 == "Package" { print $$2 }' $(CONTROL))
ifeq "$(CONTROL)" ""
$(error "Unable to find package name in $(CONTROL).")
endif

CHANGELOG := $(DEBIAN_DIR)/changelog
VERSION := $(shell awk -v 'NAME=$(NAME)' '$$1 == NAME { print $$2 ; exit }' '$(CHANGELOG)' \
	| sed -e 's/^.\([^-]*\).*$$/\1/ ' )


# Build Directory and its Contents

# This is speculative; not all packages have a source tarball.
SOURCE_TARBALL := $(NAME)-$(VERSION).tar.gz

BUILD_UNPACK_DIR := $(BUILD_DIR)/$(NAME)
$(BUILD_UNPACK_DIR): $(BUILD_DIR)
	@set -e && if [ -e "$(SOURCE_TARBALL)" ] ; \
	then \
		mkdir -p '$@' ; \
		(cd '$@' && tar xzf -) < '$(SOURCE_TARBALL)' ; \
		mv '$@/$(NAME)-$(VERSION)'/* '$@' ; \
		cp -r '$(DEBIAN_DIR)' '$@' ; \
		cp '$(SOURCE_TARBALL)' '$@' ; \
		(cd '$@' && mk-origtargz '$(SOURCE_TARBALL)') ; \
	else \
		mkdir -p '$@' ; \
		(cd '$(NAME)' && tar cf - .) | (cd '$(BUILD_UNPACK_DIR)' && tar xpf -) ; \
	fi




BUILD_DEBIAN_DIR := $(BUILD_UNPACK_DIR)/debian


# Patches

PATCHES_SERIES := $(DEBIAN_DIR)/patches/series
PATCHES := $(shell [ -e '$(PATCHES_SERIES)' ] && sed -e '/^\s*\#/d' '$(PATCHES_SERIES)')
BUILD_PATCHES_DIR := $(BUILD_DEBIAN_DIR)/patches
BUILD_PATCHES := $(PATCHES:%=$(BUILD_PATCHES_DIR)/%)

$(BUILD_PATCHES_DIR):
	mkdir -p $@

$(BUILD_PATCHES_DIR)/%: ./%
	cp -f $< $@


# Targets


# cd $(BUILD_UNPACK_DIR) 

build: $(BUILD_UNPACK_DIR) $(BUILD_PATCHES_DIR) $(BUILD_PATCHES) $(PRODUCTS_DIR)
	date | tee -a '$(BUILD_LOG)'
	@printf "\n\n#\n# Install Dependencies\n#\n\n" | tee -a '$(BUILD_LOG)'
	@cd $(BUILD_UNPACK_DIR) && mk-build-deps -i -r -s sudo 'debian/control' | tee -a '$(BUILD_LOG)'
	printf "\n\n#\n# Build Package\n#\n\n" | tee -a '$(BUILD_LOG)'
	cd $(BUILD_UNPACK_DIR) && dpkg-buildpackage --build=all \
		--root-command=fakeroot --no-sign 2>&1 | tee -a '$(BUILD_LOG)' 
	cp '$(BUILD_DIR)/$(NAME)_$(VERSION)-'* '$(PRODUCTS_DIR)'


# This target is for internal use only.
_built:
	@if [ ! -d '$(PRODUCTS_DIR)' ] ; \
	then \
		printf "\nPackage is not built.\n\n" ; \
		false ; \
	fi

install: _built
	@find '$(PRODUCTS_DIR)' -name "*.deb" \
		| xargs sudo dpkg -i


dump: _built
	@find '$(PRODUCTS_DIR)' -name "*.deb" \
	| ( \
	    while read DEB ; \
	    do \
	        echo "$$DEB" | sed -e 's|^$(PRODUCTS_DIR)/||' | xargs -n 1 printf "\n%s:\n" ; \
	        dpkg --contents "$$DEB" ; \
	        echo ; \
	    done)
