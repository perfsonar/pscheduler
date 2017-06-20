#
# Makefile for any tool class
#

NAME=bwctliperf3

FILES=\
	can-run \
	duration \
	enumerate \
	merged-results \
	participant-data \
	run \

MODULES=\
	iperf3_parser \
	iperf3_defaults \

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
