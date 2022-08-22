#
# Makefile for any tool class
#

NAME=dnspy

FILES=\
	can-run \
	duration \
	enumerate \
	merged-results \
	participant-data \
	run \

MODULES=dnspy_defaults

PYS=$(MODULES:%=%.py)
PYCS=$(MODULES:%=__pycache__/%.pyc)

$(PYCS):
ifndef PYTHON
	@echo No PYTHON specified for build
	@false
endif
	$(PYTHON) -m compileall .
TO_CLEAN += $(PYCS)



install: $(FILES) $(PYCS)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)
	install -m 444 $(PYS) $(DESTDIR)
	cp -r __pycache__ $(DESTDIR)



clean:
	rm -f $(TO_CLEAN) *~
