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
	which createrepo 2>&1 > /dev/null || yum -y install createrepo
	rm -rf $(REPO)
	./scripts/build-repo . $(REPO)
TO_CLEAN += $(REPO)

# TODO: The docs directory isn't built.


build: $(REPO)


uninstall:
	scripts/remove-all

fresh: uninstall clean build

clean:
	scripts/clean-all
	$(MAKE) -C docs $@
	rm -rf $(TO_CLEAN)
	find . -name '*~' | xargs rm -f
