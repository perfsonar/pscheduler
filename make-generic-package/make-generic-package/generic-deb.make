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
	mkdir -p '$@'
	@if [ -e "$(SOURCE_TARBALL)" ] ; \
	then \
		echo "Building from tarball." ; \
		(cd '$@' && tar xzf -) < '$(SOURCE_TARBALL)' ; \
		mv '$@/$(NAME)-$(VERSION)'/* '$@' ; \
		cp '$(SOURCE_TARBALL)' '$@' ; \
		cp -r '$(DEBIAN_DIR)' '$@' ; \
		(cd '$@' && mk-origtargz '$(SOURCE_TARBALL)') ; \
	elif [ -e "$(NAME)" ] ; \
	then \
		echo "Building from source directory." ; \
		(cd '$(NAME)' && tar cf - .) | (cd '$@' && tar xpf -) ; \
		cp -r '$(DEBIAN_DIR)' '$@/debian' ; \
	else \
		echo "No tarball or source directory." ; \
		cp -r '$(DEBIAN_DIR)' '$@/debian' ; \
	fi



BUILD_DEBIAN_DIR := $(BUILD_UNPACK_DIR)/debian
$(BUILD_DEBIAN_DIR):
	mkdir -p $@
TO_BUILD += $(BUILD_DEBIAN_DIR)


# Patches

# TODO: Need to handle global and Debian-only patches

PATCHES_SERIES := $(DEBIAN_DIR)/patches/series
PATCHES := $(shell [ -e '$(PATCHES_SERIES)' ] && sed -e '/^\s*\#/d' '$(PATCHES_SERIES)')
BUILD_PATCHES_DIR := $(BUILD_DEBIAN_DIR)/patches
BUILD_PATCHES := $(PATCHES:%=$(BUILD_PATCHES_DIR)/%)

$(BUILD_PATCHES_DIR):
	mkdir -p $@

$(BUILD_PATCHES_DIR)/%: %
	cp -f $< $@

ifneq "$(PATCHES)" ""
TO_BUILD += $(BUILD_PATCHES_DIR) $(BUILD_PATCHES)
endif

# Targets


# This is detritus from mk-build-deps
BUILD_DEPS_PACKAGE := $(NAME)-build-deps

build: $(BUILD_UNPACK_DIR) $(TO_BUILD) $(PRODUCTS_DIR)
	date | tee -a '$(BUILD_LOG)'
	@printf "\nInstall Dependencies\n\n" | tee -a '$(BUILD_LOG)'
	@cd $(BUILD_UNPACK_DIR) \
		&& mk-build-deps --install --tool 'apt-get --yes --no-install-recommends' \
		       --remove -s sudo 'debian/control' \
		| tee -a '$(BUILD_LOG)'
	@if dpkg -S '$(BUILD_DEPS_PACKAGE)' > /dev/null 2> /dev/null ; \
	then \
		echo 'Removing $(BUILD_DEPS_PACKAGE)' ; \
		sudo dpkg --remove '$(BUILD_DEPS_PACKAGE)' ; \
	fi
	printf "\nBuild Package\n\n" | tee -a '$(BUILD_LOG)'
	cd $(BUILD_UNPACK_DIR) && dpkg-buildpackage --build=all \
		--root-command=fakeroot --no-sign 2>&1 \
		| tee -a '$(BUILD_LOG)'
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
