#
# Makefile for PyJQ Debian/Ubuntu Packaging
#

default: build

OS_DISTRO := $(shell unibuild macros DISTRO)
OS_MAJOR := $(shell unibuild macros MAJOR)

FILES := \
	compat \
	control \
	gbp.conf \
	rules

OS_SUFFIX := $(OS_DISTRO)-$(OS_MAJOR)
$(FILES): FORCE
	@if [ ! -e '$@-$(OS_SUFFIX)' ] ; \
	then \
		echo 'Missing $@ for $(OS_DISTRO) $(OS_MAJOR) ($@-$(OS_SUFFIX))'; \
		exit 1 ; \
	fi
	rm -f '$@'
	cp '$@-$(OS_SUFFIX)' '$@'
TO_CLEAN += $(FILES)

build: $(FILES)

FORCE:


clean:
	rm -f $(TO_CLEAN)
