#
# Makefile for subdirectories
#

SUBDIRS=\
	database \
	programs


default: build


build install clean::
	@for DIR in $(SUBDIRS) ; \
	do \
		echo ; \
		echo Making $@ in $$DIR; \
		echo ; \
		$(MAKE) -C $$DIR $@ || break; \
	done
	@echo
	@echo Done
	@echo


clean::
	rm -f *~
