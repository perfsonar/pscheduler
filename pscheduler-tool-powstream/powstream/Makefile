#
# Makefile for any tool class
#

NAME=powstream

FILES=\
	can-run \
	duration \
	enumerate \
	merged-results \
	powstream_defaults.py\
	powstream_utils.py\
	participant-data \
	run \


CONFS=\
	$(NAME).conf


install: $(FILES) $(CONFS)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
ifdef CONFS
ifndef CONFDIR
	@echo No CONFDIR specified for installation
	@false
endif
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)
ifdef CONFS
	mkdir -p $(CONFDIR)
	install -m 644 $(CONFS) $(CONFDIR)
endif


clean:
	rm -f $(TO_CLEAN) *~
