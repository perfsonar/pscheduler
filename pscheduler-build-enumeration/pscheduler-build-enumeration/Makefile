#
# Makefile for pscheduiler-build-enumeration
#

NAME=pscheduler-build-enumeration

default:
	@echo Nothing to do.


install: $(NAME)
ifndef BINDIR
	@echo No BINDIR specified for installation
	@false
endif
	mkdir -p $(BINDIR)
	install -m 555 $(NAME) $(BINDIR)


clean:
	rm -f $(TO_CLEAN) *~
