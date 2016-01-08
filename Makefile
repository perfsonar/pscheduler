#
# Makefile for pScheduler top-level directory
#

default: build


# TODO: The docs directory isn't built.
build:
	scripts/build-all


# TODO: Need to build the repository index.
REPO=./repo
repo: build
	rm -rf $(REPO)
	mkdir -p $(REPO)
	cp */*.rpm $(REPO)
TO_CLEAN += $(REPO)

uninstall:
	scripts/remove-all

clean:
	scripts/clean-all
	$(MAKE) -C docs $@
	rm -rf $(TO_CLEAN)
	find . -name '*~' | xargs rm -f
