#
# Makefile for any test class
#

NAME=throughput

FILES=\
	cli-to-spec \
	enumerate \
	participants \
	result-format \
	spec-format \
	spec-is-valid \
        spec-to-cli \
        limit-is-valid \
        limit-passes \

MODULES=\
        throughput_utils \
	validate \



PYS=$(MODULES:%=%.py)
PYCS=$(MODULES:%=%.pyc)

$(PYCS):
	python -m compileall .
TO_CLEAN += $(PYCS)


install: $(FILES) $(PYS) $(PYCS)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)
	install -m 444 $(PYS) $(PYCS) $(DESTDIR)


clean:
	rm -f $(TO_CLEAN) *~
