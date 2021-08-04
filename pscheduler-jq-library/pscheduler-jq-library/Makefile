#
# Makefile for pScheduler JQ library
#

#
# The following variables need to be specified when running this
# Makefile:
#
#   DESTDIR             Where the files should be installed
#

MODULES=\
	iso8601 \
	si


default:  build

build:
	@true

install: build
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 444 $(MODULES:%=%.jq) $(DESTDIR)

clean:
	rm -rf $(TO_CLEAN) *~
