#
# Makefile for pScheduler top-level directory
#

default: build


SOURCES_DIR=./SRPMS
srpms::
	rm -rf $(SOURCES_DIR)
	mkdir -p $(SOURCES_DIR)
	./scripts/build-sources $(SOURCES_DIR)
TO_CLEAN += $(SOURCES_DIR)



BUILD_LOG=build.log

# The shell command below does the equivalent of BASH's pipefail
# within the confines of POSIX.
# Source: https://unix.stackexchange.com/a/70675/15184
packages:
	((( \
	(./scripts/build-all; echo $$? >&3) \
	| tee $(BUILD_LOG) >&4) 3>&1) \
	| (read XS; exit $$XS) \
	) 4>&1
TO_CLEAN += $(BUILD_LOG)


REPO=./REPO
$(REPO): packages
	which createrepo > /dev/null 2>&1 || yum -y install createrepo
	rm -rf $(REPO)
	./scripts/build-repo . $(REPO)
TO_CLEAN += $(REPO)

# TODO: The docs directory isn't built.


build: $(REPO)


# The three makes here install the things that are needed to RPM specs
# to be read properly.  They're uninstalled at the end.
uninstall:
	$(MAKE) -C rpm-with-deps clean build install clean
	$(MAKE) -C make-generic-package clean build install clean
	$(MAKE) -C pscheduler-rpm clean build install clean
	scripts/remove-all

fresh: uninstall build

clean:
	scripts/clean-all
	$(MAKE) -C docs $@
	rm -rf $(TO_CLEAN)
	find . -name '*~' | xargs rm -f
