#
# Generic Makefile for RPMs
#


#
# NO USER-SERVICEABLE PARTS BELOW THIS LINE
#

ifndef GENERIC_PACKAGE_MAKE
$(error "Include generic-package.make, not an environment-specific template.")
endif


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
VERSION := $(shell rpmspec -P "$(SPEC)" | awk '$$1 == "Version:" { print $$2 }')
SOURCE_FILES := $(shell spectool -S $(SPEC) | awk '{ print $$2 }')
PATCH_FILES := $(shell spectool -P $(SPEC) | awk '{ print $$2 }')


#
# Automagic source tarball construction
# TODO: Move to common
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
ALL_TARBALLS=$(TARBALL_SOURCE)-*.tar.gz

$(TARBALL):
	cp -r $(TARBALL_SOURCE) $(TARBALL_NAME)
	tar czf $@ $(TARBALL_NAME)
	rm -rf $(TARBALL_NAME)

BUILD_DEPS += $(TARBALL)
TO_CLEAN += $(TARBALL) $(TARBALL_NAME) $(ALL_TARBALLS)

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


BUILD_ROOT=./BUILD-ROOT
$(BUILD_ROOT):
	mkdir -p $@
TO_CLEAN += $(BUILD_ROOT)


ifdef NO_DEPS
  RPM=rpm
  RPMBUILD=rpmbuild
else
  RPM=rpm-with-deps
  RPMBUILD=rpmbuild-with-deps
endif



#
# Useful Targets
#

build:: $(BUILD_DEPS) $(BUILD_DIR) $(BUILD_ROOT)
	set -o pipefail \
                && HOME=$(shell pwd) \
                   $(RPMBUILD) -ba \
			--buildroot $(shell cd $(BUILD_ROOT) && pwd) \
			$(SPEC) 2>&1 \
		| tee build.log
	find $(BUILD_DIR) -name '*.rpm' | xargs -I{} cp {} .
TO_CLEAN += build.log
TO_CLEAN += *.rpm



srpm:: $(BUILD_DEPS) $(BUILD_DIR)
	HOME=$(shell pwd) rpmbuild -v -bs $(RPMBUILD_OPTS) $(SPEC)
	find $(BUILD_DIR) -name '*.src.rpm' | xargs -I{} cp {} .
TO_CLEAN += *.src.rpm



dump::
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


install::
	find $(BUILD_RPMS) -name '*.rpm' | xargs $(RPM) -Uvh --force



clean::
	find . -depth -name Makefile \
	    -exec /bin/sh -c \
	    '[ "{}" != "./Makefile" ] && make -C `dirname {}` clean' \;


# Placeholder for running unit tests.
test::
	@true

