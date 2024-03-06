#
# Makefile for Testbed
#

PRODUCT := testbed.json

# Each subdirectory's Makefile produces a file called "output.json"
SUBDIRS := \
	skeleton \
	members \
	plugins \
	schedules


default: build


$(PRODUCT)::
	@set -e && for SUBDIR in $(SUBDIRS) ; \
	do \
		printf "\n#\n# Building $$SUBDIR\n#\n\n" ; \
		$(MAKE) -C "$${SUBDIR}" ; \
	done
	printf "\n#\n# Merging results\n#\n\n"
	./bin/merge-json $(SUBDIRS:%=%/output.json) \
		| ./bin/finish \
		> "$@"
TO_CLEAN += $(PRODUCT)


build: $(PRODUCT)


clean:
	@set -e && for SUBDIR in $(SUBDIRS) ; \
	do \
		$(MAKE) -C "$${SUBDIR}" "$@" ; \
	done
	rm -rf $(TO_CLEAN)
	find . -name '*~' | xargs rm -rf
