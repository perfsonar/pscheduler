#
# Makefile for any test class
#

NAME=throughput

FILES=\
	cli-to-spec \
	enumerate \
	participants \
	result-format \
	spec-format \
	spec-is-valid \
	spec-to-cli \


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
