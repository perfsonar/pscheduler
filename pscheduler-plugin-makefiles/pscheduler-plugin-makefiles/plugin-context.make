#
# Makefile for any archiver class
#

ENUMERATE := enumerate
ENUMERATE_JSON := enumerate.json
ENUMERATE_SKELETON := enumerate-skeleton.json
SPEC_SCHEMA := spec-jsonschema.json
UI_SCHEMA := spec-uischema.json

FILES += \
	$(ENUMERATE) \
	$(ENUMERATE_JSON) \
	data-is-valid \
	change

default: build

$(ENUMERATE): $(ENUMERATE_SKELETON) $(SPEC_SCHEMA) $(UI_SCHEMA)
	pscheduler-build-enumeration \
		--plain .=$(ENUMERATE_SKELETON) \
		--validator .spec.jsonschema=$(SPEC_SCHEMA) \
		--plain .spec.uischema=$(UI_SCHEMA) \
		> $@
	chmod +x $@
TO_CLEAN += $(ENUMERATE)


$(ENUMERATE_JSON): $(ENUMERATE)
	./$< > $@
TO_CLEAN += $(ENUMERATE_JSON)


build: $(FILES)


install:build
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)


clean:
	rm -f $(TO_CLEAN) *~
