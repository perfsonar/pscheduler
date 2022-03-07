#
# Makefile for any archiver class
#

NAME=postgresql

# TODO: This should be an includable template.

FILES=\
	enumerate \
	data-is-valid \
	archive

DOCS=\
	$(NAME).txt




install: $(FILES) $(DOCS)
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
	install -m 555 $(FILES) $(DESTDIR)
ifdef DOCS
	mkdir -p $(DOCDIR)
	install -m 444 $(DOCS) $(DOCDIR)
endif



clean:
	rm -f $(TO_CLEAN) *~
