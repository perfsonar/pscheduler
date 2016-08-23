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


packages:
	scripts/build-all | tee build.log
TO_CLEAN += build.log


REPO=./REPO
repo: packages
	which createrepo 2>&1 > /dev/null || yum -y install createrepo
	rm -rf $(REPO)
	./scripts/build-repo . $(REPO)
TO_CLEAN += $(REPO)

# TODO: The docs directory isn't built.


build: repo


uninstall:
	scripts/remove-all

fresh: uninstall clean build

clean:
	scripts/clean-all
	$(MAKE) -C docs $@
	rm -rf $(TO_CLEAN)
	find . -name '*~' | xargs rm -f
