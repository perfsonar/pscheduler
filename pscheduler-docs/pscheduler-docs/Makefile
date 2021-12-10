#
# Makefile for pscheduler-docs
#

FILES=\

SUBDIRS=\
	limit-examples

default:
	for SUBDIR in $(SUBDIRS) ; do $(MAKE) -C $$SUBDIR ; done


install: $(FILES) $(SUBDIRS)
ifndef DOCDIR
	@echo No DOCDIR specified for installation
	@false
endif
	mkdir -p $(DOCDIR)
ifneq ($(FILES),)
	install -m 555 $(FILES) $(DOCDIR)
endif
	cp -r $(SUBDIRS) $(DOCDIR)
	find $(DOCDIR) -type f | xargs chmod 444


clean:
	rm -f $(TO_CLEAN) *~
