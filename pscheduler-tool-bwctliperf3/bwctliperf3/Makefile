#
# Makefile for any tool class
#

NAME=bwctliperf3

FILES=\
	can-run \
	duration \
	enumerate \
	merged-results \
	participant-data \
	run \
	iperf3_parser.py \
	iperf3_defaults.py\



install: $(FILES)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)


clean:
	rm -f $(TO_CLEAN) *~
