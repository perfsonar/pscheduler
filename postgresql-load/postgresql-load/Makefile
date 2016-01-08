#
# Makefile for postgresql-load
#

NAME=postgresql-load

default:
	@echo Nothing to do.


install: $(NAME) $(NAME).1
ifndef BINDIR
	@echo No BINDIR specified for installation
	@false
endif
ifndef MANDIR
	@echo No MANDIR specified for installation
	@false
endif
	mkdir -p $(BINDIR)
	install -m 555 $(NAME) $(BINDIR)
	mkdir -p $(MANDIR)/man1
	install -m 444 $(NAME).1 $(MANDIR)/man1


clean:
	rm -f $(TO_CLEAN) *~