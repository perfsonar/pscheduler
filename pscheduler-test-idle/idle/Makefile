#
# Makefile for any test class
#

NAME=idle

# TODO: Everything below this should be made into a template that can
# be included.

FILES=\
	cli-to-spec \
	enumerate \
	participants \
	result-format \
	spec-format \
	spec-is-valid \
	spec-to-cli

MODULES=\
	validate \


default: build

### TODO: THIS PIECE SHOULD BE INCLUDABLE

PS_DICT := pscheduler-dictionary.json
$(PS_DICT)::
	pscheduler internal json-dictionary > $@
TO_CLEAN += $(PS_DICT)


SPEC_SCHEMA := spec-schema.json
DEREFED_SPEC := spec-schema-deref.json
$(DEREFED_SPEC): $(PS_DICT) $(SPEC_SCHEMA)
	jsonschematool --pretty  --dereference $(PS_DICT) $(SPEC_SCHEMA) > $@
TO_CLEAN := $(DEREFED_SPEC)


ENUMERATE := enumerate
ENUMERATE_JSON := enumerate.json

$(ENUMERATE): $(ENUMERATE_JSON) $(DEREFED_SPEC)
	pscheduler-build-enumeration $^ > $@
	chmod +x $@
TO_CLEAN += $(ENUMERATE)


### END TODO

PYS=$(MODULES:%=%.py)
PYCS=$(MODULES:%=__pycache__/%.pyc)

$(PYCS):
ifndef DESTDIR
	@echo No DESTDIR specified for build
	@false
endif
	$(PYTHON) -m compileall .
TO_CLEAN += $(PYCS) __pycache__


build: $(FILES) $(PYS) $(PYCS)


install: build
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)
	install -m 444 $(PYS) $(DESTDIR)
	cp -r __pycache__ $(DESTDIR)


clean:
	rm -rf $(TO_CLEAN) *~
