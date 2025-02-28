#
# Makefile for json2pickle
#

PROGRAMS := \
	json2pickle \
	pickle2json

MANS := $(PROGRAMS:%=%.1)

default:
	@echo Nothing to do.


install: $(PROGRAMS) $(MANS)
ifndef BINDIR
	@echo No BINDIR specified for installation
	@false
endif
ifndef MANDIR
	@echo No MANDIR specified for installation
	@false
endif
	mkdir -p $(BINDIR)
	install -m 555 $(PROGRAMS) $(BINDIR)
	mkdir -p $(MANDIR)/man1
	install -m 444 $(MANS) $(MANDIR)/man1


clean:
	rm -f $(TO_CLEAN) *~
