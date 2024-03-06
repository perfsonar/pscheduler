#
# Makefile for Testbed Members
#

PRODUCT := output.json


default: build

MEMBERS := members

BUILDER := ./build-addresses
$(PRODUCT): Makefile $(BUILDER) $(MEMBERS)
	$(BUILDER) < '$(MEMBERS)' > "$@"
TO_CLEAN += $(PRODUCT)


build: $(PRODUCT)


clean:
	rm -rf $(TO_CLEAN) *~
