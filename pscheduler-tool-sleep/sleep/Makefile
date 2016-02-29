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
