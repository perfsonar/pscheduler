#
# Makefile for pScheduler top-level directory
#

default: build



BUILD_LOG=LOG
TO_CLEAN += $(BUILD_LOG)

# The shell command below does the equivalent of BASH's pipefail
# within the confines of POSIX.
# Source: https://unix.stackexchange.com/a/70675/15184
packages:
	((( \
	(./scripts/build-all; echo $$? >&3) \
	| tee $(BUILD_LOG) >&4) 3>&1) \
	| (read XS; exit $$XS) \
	) 4>&1



# TODO: Should this do anything to turn the products into a
# functioning repository for RH or Debian?

PRODUCTS=PRODUCTS
$(PRODUCTS): packages
	rm -rf "$@"
	mkdir -p "$@"
	find . -type f | egrep -e '^./[^/]*/PRODUCTS/' \
		| xargs -I{} cp {} '$@'

TO_CLEAN += $(PRODUCTS)



# TODO: The docs directory isn't built.


build: $(PRODUCTS)



# TODO: These targets are still RPM-specific

# The three makes here install the things that are needed to RPM specs
# to be read properly.  They're uninstalled at the end.
uninstall:
	$(MAKE) -C rpm-with-deps clean build install clean
	$(MAKE) -C make-generic-package clean build install clean
	$(MAKE) -C pscheduler-rpm clean build install clean
	scripts/remove-all

fresh: uninstall build

clean:
	$(MAKE) -C rpm-with-deps clean build install clean
	$(MAKE) -C make-generic-package clean build install clean
	scripts/build-all $@
	$(MAKE) -C docs $@
	rm -rf $(TO_CLEAN)
	find . -name '*~' | xargs rm -f
