#
# Makefile for Testbed
#

PRODUCT := testbed.json

# Each subdirectory's Makefile produces a file called "output.json"
SUBDIRS := \
	schedules


default: build

$(PRODUCT): Makefile
	@for SUBDIR in $(SUBDIRS) ; \
	do \
		printf "\n#\n# Building $$SUBDIR\n#\n\n" ; \
		$(MAKE) -C "$${SUBDIR}" ; \
	done
	printf "\n#\n# Merging results\n#\n\n"
	jq -s add $(SUBDIRS:%=%/output.json) > "$@"
TO_CLEAN += $(PRODUCT)


build: $(PRODUCT)


clean:
	@for SUBDIR in $(SUBDIRS) ; \
	do \
		$(MAKE) -C "$${SUBDIR}" "$@" ; \
	done
	rm -rf $(TO_CLEAN) *~
