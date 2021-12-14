#
# Makefile for any test class
#

NAME=latency

FILES=\
	cli-to-spec \
	enumerate \
	limit-is-valid \
	limit-passes \
	participants \
	result-format \
	spec-format \
	spec-is-valid \
	spec-to-cli \

MODULES=\
	latency_utils \
	validate \

PYS=$(MODULES:%=%.py)
PYCS=$(MODULES:%=__pycache__/%.pyc)

$(PYCS):
ifndef DESTDIR
	@echo No PYTHON specified for build
	@false
endif
	$(PYTHON) -m compileall .
TO_CLEAN += $(PYCS)



install: $(FILES) $(PYS) $(PYCS)
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
