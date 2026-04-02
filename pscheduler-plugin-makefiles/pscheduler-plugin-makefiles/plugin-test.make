#
# Makefile for any test class
#

ENUMERATE := enumerate
ENUMERATE_JSON := enumerate.json
ENUMERATE_SKELETON := enumerate-skeleton.json
SPEC_SCHEMA := spec-schema.json

FILES += \
	cli-to-spec \
	$(ENUMERATE) \
	$(ENUMERATE_JSON) \
	participants \
	result-format \
	spec-format \
	spec-is-valid \
	spec-to-cli


MODULES += \
	validate


default: build



$(ENUMERATE): $(ENUMERATE_SKELETON) $(SPEC_SCHEMA)
	pscheduler-build-enumeration $^ > $@
	chmod +x $@
TO_CLEAN += $(ENUMERATE)

$(ENUMERATE_JSON): $(ENUMERATE)
	./$< > $@
TO_CLEAN += $(ENUMERATE_JSON)


PYS=$(MODULES:%=%.py)
PYCS=$(MODULES:%=__pycache__/%.pyc)

$(PYCS):
ifndef PYTHON
	@echo No PYTHON specified for build
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
