#
# Makefile for any context changer class
#

NAME=null

# TODO: This should be an includable template.

FILES=\
	enumerate \
	data-is-valid \
	change


install: $(FILES)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)


clean:
	rm -f $(TO_CLEAN) *~
