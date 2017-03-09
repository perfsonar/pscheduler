#
# Makefile for any tool class
#

NAME=sleep

# TODO: Everything below this should be made into a template that can
# be included.

FILES=\
	can-run \
	duration \
	enumerate \
	participant-data \
	run \
	merged-results \


install: $(FILES)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)


clean:
	rm -f $(TO_CLEAN) *~
