#
# Generic Makefile for RPMs
#
# To use this file, create a Makefile containing the following:
#
#     inclulde make/generic-rpm.make
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

#
# Spec file and things derived from it
#

# Do this in a POSIX-y way, which precludes mindepth.
SPEC := $(shell find . -name '*.spec' | sed -e '/^\.\/[^/]*$$/!d; s/^\.\///')

ifeq "$(words $(SPEC))" "0"
  $(error No spec in this directory)
endif
ifneq "$(words $(SPEC))" "1"
  $(error This directory contains more than one spec file)
endif

NAME := $(shell echo "$(SPEC)" | sed -e 's/\.spec$$//')
VERSION := $(shell awk '$$1 == "Version:" { print $$2 }' $(SPEC))
SOURCE_FILES := $(shell spectool -S $(SPEC) | awk '{ print $$2 }')
PATCH_FILES := $(shell spectool -P $(SPEC) | awk '{ print $$2 }')


#
# Automagic source tarball construction
#

ifdef AUTO_TARBALL

    ifeq "$(words $(SOURCE_FILES))" "0"
        $(error No need to set AUTO_TARBALL with no sources in spec file)
    endif

    ifeq "$(shell [ $(words $(SOURCE_FILES)) -gt 1 ]; echo $$?)" "0"
        $(error Cannot automatically build a tarball from multiple sources)
    endif

    ifneq "$(findstring -, $(VERSION))" ""
        $(error The version number in the spec may not contain hyphens.)
    endif


TARBALL_SOURCE=$(shell echo $(SOURCE_FILES) | sed -e 's/-[^-]*\.tar\.gz$$//')
TARBALL_NAME=$(TARBALL_SOURCE)-$(VERSION)
TARBALL=$(TARBALL_NAME).tar.gz
$(TARBALL):
	cp -r $(TARBALL_SOURCE) $(TARBALL_NAME)
	tar czf $@ $(TARBALL_NAME)
	rm -rf $(TARBALL_NAME)

BUILD_DEPS += $(TARBALL)
TO_CLEAN += $(TARBALL) $(TARBALL_NAME)

endif


#
# RPM Build Directory
#

BUILD_DIR=./rpmbuild
BUILD_BUILD=$(BUILD_DIR)/BUILD
BUILD_RPMS=$(BUILD_DIR)/RPMS
BUILD_SOURCES=$(BUILD_DIR)/SOURCES
BUILD_SPECS=$(BUILD_DIR)/SPECS
BUILD_SRPMS=$(BUILD_DIR)/SRPMS

BUILD_SUBS=\
	$(BUILD_BUILD) \
	$(BUILD_RPMS) \
	$(BUILD_SOURCES) \
	$(BUILD_SPECS) \
	$(BUILD_SRPMS) \

$(BUILD_DIR): $(SPEC) $(SOURCE_FILES)
	rm -rf $@
	mkdir -p $(BUILD_SUBS)
	cp $(SPEC) $(BUILD_SPECS)
ifneq "$(words $(SOURCE_FILES))" "0"
	cp $(SOURCE_FILES) $(BUILD_SOURCES)
endif
ifneq "$(words $(PATCH_FILES))" "0"
	cp $(PATCH_FILES) $(BUILD_SOURCES)
endif
TO_CLEAN += $(BUILD_DIR)


BUILD_ROOT=./BUILD-ROOT
$(BUILD_ROOT):
	mkdir -p $@
TO_CLEAN += $(BUILD_ROOT)



#
# Useful Targets
#

build: $(BUILD_DEPS) $(BUILD_DIR) $(BUILD_ROOT)
	set -o pipefail \
                && HOME=$(shell pwd) \
                   rpmbuild -ba \
			--buildroot $(shell cd $(BUILD_ROOT) && pwd) \
			$(SPEC) 2>&1 \
		| tee build.log
	find $(BUILD_DIR) -name '*.rpm' | xargs -I{} cp {} .
TO_CLEAN += build.log
TO_CLEAN += *.rpm


rpmdump:
	@if [ -d "$(BUILD_RPMS)" ] ; then \
	    for RPM in `find $(BUILD_RPMS) -name '*.rpm'` ; do \
	    	echo `basename $${RPM}`: ; \
	     	rpm -qpl $$RPM 2>&1 | sed -e 's/^/\t/' ; \
	     	echo ; \
	    done ; \
        else \
	    echo "RPMs are not built." ; \
	    false ; \
	fi


install:
	find $(BUILD_RPMS) -name '*.rpm' | xargs rpm -Uvh --force


clean:
ifdef AUTO_TARBALL
	@if [ -f "${NAME}/Makefile" ] ; then \
		$(MAKE) -C $(NAME) clean ; \
	fi
endif
	rm -rf $(TO_CLEAN) *~



#
# Convenient shorthands
#

b: build
c: clean
i: install
r: rpmdump

cb: c b
cbr: c b r
cbi: c b i

# CBI with forced clean afterward
cbic: cbi
	$(MAKE) clean

# CBR with forced clean afterward
cbrc: cbr
	$(MAKE) clean
