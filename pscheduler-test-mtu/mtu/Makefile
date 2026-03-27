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

ENUMERATE := enumerate
ENUMERATE_JSON := enumerate.json
SPEC_SCHEMA := spec-schema.json

$(ENUMERATE): $(ENUMERATE_JSON) $(SPEC_SCHEMA)
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
