#
# Makefile for any tool class
#

NAME := pstimer

PROGRAMS := \
	can-run \
	duration \
	enumerate \
	merged-results \
	participant-data \
	run


FILES := $(PROGRAMS)


install: $(FILES)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false

endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)

clean:
	rm -rf $(TO_CLEAN) *~
