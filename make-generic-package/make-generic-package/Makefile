#
# Makefile for make-generic-package
#

default: build

build:
	@echo Nothing to do here.


$(DESTDIR):
	mkdir -p $(DESTDIR)


install: $(DESTDIR)
	install -m 444 *.make $(DESTDIR)


clean:
	rm -f *~
