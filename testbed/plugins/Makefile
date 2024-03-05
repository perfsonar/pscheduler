#
# Makefile for Testbed Plugins
#

PRODUCT := output.json

# Top of the source tree
TOP := ../..


default: build


WORK := work
$(WORK)::
	rm -rf "$@"
	mkdir -p "$@"
TO_CLEAN += $(WORK)


BUILDER := ./copy-plugin-json
$(PRODUCT): Makefile $(BUILDER) $(WORK)
	$(BUILDER) '$(TOP)' '$(WORK)'
	jq -s add $(WORK)/* > $@
TO_CLEAN += $(PRODUCT)


build: $(PRODUCT)


clean:
	rm -rf $(TO_CLEAN) *~
