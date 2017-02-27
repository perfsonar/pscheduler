#
# Makefile for any archiver class
#

NAME=failer

FILES=\
	enumerate \
	data-is-valid \
	archive

install: $(FILES)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)



clean:
	rm -f $(TO_CLEAN) *~
