#
# Makefile for any archiver class
#

NAME=esmond

# TODO: This should be an includable template.

FILES=\
	enumerate \
	data-is-valid \
	archive

MODULES=\
	esmond_util \

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
