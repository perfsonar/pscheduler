#
# Makefile for any tool class
#

FILES=\
	can-run \
	duration \
	enumerate \
	merged-results \
	participant-data \
	run \
	ping_utils.py



install: $(FILES)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)


clean:
	rm -f $(TO_CLEAN) *~
