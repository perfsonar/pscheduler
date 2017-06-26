#
# Makefile for any tool class
#

NAME=nuttcp

FILES=\
	can-run \
	duration \
	enumerate \
	merged-results \
	participant-data \
	run \

MODULES=\
	nuttcp_parser \
	nuttcp_defaults \
	nuttcp_utils \

PYS=$(MODULES:%=%.py)
PYCS=$(MODULES:%=%.pyc)

$(PYCS):
	python -m compileall .
TO_CLEAN += $(PYCS)


CONFS=\
	$(NAME).conf

install: $(FILES) $(CONFS) $(PYS) $(PYCS)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
ifdef CONFS
ifndef CONFDIR
	@echo No CONFDIR specified for installation
	@false
endif
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)
	install -m 444 $(PYS) $(PYCS) $(DESTDIR)
ifdef CONFS
	mkdir -p $(CONFDIR)
	install -m 644 $(CONFS) $(CONFDIR)
endif


clean:
	rm -f $(TO_CLEAN) *~
