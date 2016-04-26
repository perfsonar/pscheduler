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

MODULES=\
	validate \

DOCS=



FILES += $(MODULES:%=%.py)
PYCS=$(MODULES:%=%.pyc)

$(PYCS):
	python -m compileall .
TO_CLEAN += $(PYCS)


install: $(FILES) $(PYCS) $(DOCS)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
ifdef DOCS
ifndef DOCDIR
	@echo No DOCDIR specified for installation
	@false
endif
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(PYCS) $(DESTDIR)
ifdef DOCS
	mkdir -p $(DOCDIR)
	install -m 444 $(DOCS) $(DOCDIR)
endif


clean:
	rm -f $(TO_CLEAN) *~
