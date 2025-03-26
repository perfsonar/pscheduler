#
# Makefile for jsconschematool sample
#

COMBINED := combined.json
SCHEMAS := dictionary.json schema.json

default: build

$(COMBINED): $(SCHEMAS)
	../jsonschematool --pretty --dereference $(SCHEMAS) > $@

build: $(COMBINED)
	cat $<


TO_CLEAN += $(COMBINED)

clean:
	rm -rf $(TO_CLEAN) *~
