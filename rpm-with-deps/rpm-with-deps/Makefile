#
# Makefile for rpm-with-deps
#

NAME=rpm-with-deps

# TODO: This is an ugly hack to deal with the fact that VirtualBox
# guests do not, by default, allow the creation of symbolic links in
# shared folders.
COPIES=rpmbuild-with-deps

default:
	@true


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
	for COPY in $(COPIES) ; \
	do \
		install -m 555 $(NAME) $(BINDIR)/$$COPY ; \
	done
	mkdir -p $(MANDIR)
	install -m 444 $(NAME).1 $(MANDIR)


clean:
	rm -f $(TO_CLEAN) *~
