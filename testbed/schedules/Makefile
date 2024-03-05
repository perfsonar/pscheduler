#
# Makefile for Testbed Schedules
#

PRODUCT := output.json

INTERVALS := intervals


default: build


BUILDER := ./build-schedules
$(PRODUCT): Makefile $(BUILDER) $(INTERVALS)
	$(BUILDER) $(BUILDER_ARGS) < $(INTERVALS) > "$@"
TO_CLEAN += $(PRODUCT)


build: $(PRODUCT)


clean:
	rm -rf $(TO_CLEAN) *~
