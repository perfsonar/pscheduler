#
# Makefile for pScheduler Plugin Makefiles
#

default:
	@echo Nothing to do.

FILES := $(wildcard *.make)


install: $(FILES)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	cp -f $(FILES) $(DESTDIR)
	chmod 444 $(FILES:%=$(DESTDIR)/%)


clean:
	rm -f $(TO_CLEAN) *~
