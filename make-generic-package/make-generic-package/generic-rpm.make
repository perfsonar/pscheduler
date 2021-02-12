#
# Generic Makefile for RPMs
#


#
# NO USER-SERVICEABLE PARTS BELOW THIS LINE
#

ifndef GENERIC_PACKAGE_MAKE
$(error "Include generic-package.make, not an environment-specific template.")
endif


# RPM Directory

RPM_DIR := $(shell find . -type d -name "rpm" | egrep -ve '^$(BUILD_DIR)')
ifeq "$(RPM_DIR)" ""
$(error "Unable to find rpm directory.")
endif
ifneq "$(words $(RPM_DIR))" "1"
$(error "Found more than one rpm directory.  There can be only one.")
endif


# Spec file and things derived from it

SPEC := $(shell find '$(RPM_DIR)' -name '*.spec')
SPEC_BASE := $(notdir $(SPEC))

ifeq "$(words $(SPEC))" "0"
  $(error No spec in the $(RPM_DIR) directory)
endif
ifneq "$(words $(SPEC))" "1"
  $(error $(RPM_DIR) contains more than one spec file)
endif

VERSION := $(shell rpm -q --queryformat="%{version}\n" --specfile '$(SPEC)')
SOURCE_FILES := $(shell spectool -S $(SPEC) | awk '{ print $$2 }')
PATCH_FILES := $(shell spectool -P $(SPEC) | awk '{ print $$2 }')

#
# RPM Build Directory
#

BUILD_RPMS=$(BUILD_DIR)/RPMS
BUILD_SOURCES=$(BUILD_DIR)/SOURCES
BUILD_SPECS=$(BUILD_DIR)/SPECS
BUILD_SRPMS=$(BUILD_DIR)/SRPMS

BUILD_SUBS=\
	$(BUILD_RPMS) \
	$(BUILD_SOURCES) \
	$(BUILD_SPECS) \
	$(BUILD_SRPMS)


TO_BUILD += $(BUILD_SUBS)

# Source files installed int he build directory
INSTALLED_SOURCE_FILES := $(SOURCE_FILES:%=$(BUILD_SOURCES)/%)

$(BUILD_SUBS):
	mkdir -p '$@'

$(BUILD_DIR):: $(SPEC) $(INSTALLED_SOURCE_FILES) $(PATCH_FILES) $(BUILD_SUBS)
	cp $(SPEC) $(BUILD_SPECS)
ifneq "$(words $(PATCH_FILES))" "0"
	cp $(PATCH_FILES) $(BUILD_SOURCES)
endif


# Source files

ifeq "$(words $(SOURCE_FILES))" "1"
  TARBALL_EXISTS := $(shell [ -e '$(SOURCE_FILES)' ] && echo 1 || true)
else
  # Go with whatever's in the source file.
  TARBALL_EXISTS=1
endif


ifeq "$(TARBALL_EXISTS)" "1"

# Have tarball(s), just need to copy into $(BUILD_SOURCES)

TO_BUILD += $(SOURCE_FILES:%=$(BUILD_SOURCES)/%)

$(BUILD_SOURCES)/%: % $(BUILD_SOURCES)
	cp '$(notdir $@)' '$@'

else

# Have a tarball, need to generate it in $(BUILD_SOURCES)

TARBALL_SOURCE := $(shell echo $(SOURCE_FILES) | sed -e 's/-[^-]*\.tar\.gz$$//')
TARBALL_NAME := $(TARBALL_SOURCE)-$(VERSION)
TARBALL_FULL := $(TARBALL_NAME).tar.gz

TARBALL_BUILD := $(BUILD_SOURCES)/$(TARBALL_NAME)
BUILD_SOURCE_TARBALL := $(BUILD_SOURCES)/$(TARBALL_FULL)

$(BUILD_SOURCE_TARBALL): $(BUILD_SOURCES)
	cp -r '$(TARBALL_SOURCE)' '$(TARBALL_BUILD)'
	cd '$(BUILD_SOURCES)' && tar czf '$(TARBALL_FULL)' '$(TARBALL_NAME)'
	rm -rf '$(TARBALL_BUILD)'

TO_BUILD += $(BUILD_SOURCE_TARBALL)

endif


# Spec file in the build directory

BUILD_SPEC_FILE := $(BUILD_SPECS)/$(SPEC_BASE)
$(BUILD_SPEC_FILE): $(SPEC)
	cp '$<' '$@'
TO_BUILD += $(BUILD_SPEC_FILE)



#
# Useful Targets
#

ifdef NO_DEPS
  RPM=rpm
  RPMBUILD=rpmbuild
else
  RPM=rpm-with-deps
  RPMBUILD=rpmbuild-with-deps
endif

build:: $(TO_BUILD)
	(((( \
		$(RPMBUILD) -ba \
			--define '_topdir $(shell cd $(BUILD_DIR) && pwd)' \
			$(BUILD_SPEC_FILE) 2>&1 ; \
		echo $$? >&3 \
	) \
	| tee $(BUILD_LOG) >&4) 3>&1) \
	| (read XS; exit $$XS) \
	) 4>&1
	find $(BUILD_DIR)/RPMS -name '*.rpm' | xargs -I{} cp {} '$(PRODUCTS_DIR)'
	find $(BUILD_DIR)/SRPMS -name '*.rpm' | xargs -I{} cp {} '$(PRODUCTS_DIR)'


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
	@for PACKAGE in `find $(BUILD_RPMS) -name '*.rpm'`; do \
	    SHORT=`basename "$${PACKAGE}" | sed -e 's/.rpm$$//'` ; \
	    rpm --quiet -q "$${SHORT}" && OP="reinstall" || OP="install" ; \
	    echo "$${SHORT} will be $${OP}ed" ; \
	    sudo yum -y "$${OP}" "$${PACKAGE}" ; \
	done


# Placeholder for running unit tests.
test::
	@true
