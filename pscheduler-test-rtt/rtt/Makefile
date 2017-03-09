#
# Makefile for any test class
#

NAME=trace

# TODO: Everything below this should be made into a template that can
# be included.

FILES=\
	cli-to-spec \
	enumerate \
	participants \
	result-format \
	spec-format \
	spec-is-valid \
	spec-to-cli \
	limit-is-valid \
	limit-passes\


MODULES=\
	validate \


FILES += $(MODULES:%=%.py)
PYCS=$(MODULES:%=%.pyc)

$(PYCS):
	python -m compileall .
TO_CLEAN += $(PYCS)


install: $(FILES) $(PYCS)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(PYCS) $(DESTDIR)


clean:
	rm -f $(TO_CLEAN) *~
