#
# Makefile for any tool class
#

NAME=iperf

FILES=\
	can-run \
	duration \
	enumerate \
	merged-results \
	participant-data \
	run \
	iperf2_parser.py \
        iperf2_utils.py \
        iperf2.conf \
	iperf2_defaults.py\


install: $(FILES)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)



clean:
	rm -f $(TO_CLEAN) *~
