#
# Makefile for any test class
#

NAME=latency

FILES=\
	cli-to-spec \
	enumerate \
	latency_utils.py \
	validate.py \
	participants \
	pscheduler-schema-latency-request.json \
	pscheduler-schema-latency-response.json \
	result-format \
	spec-format \
	spec-is-valid \
	spec-to-cli \



install: $(FILES)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)


clean:
	rm -f $(TO_CLEAN) *~
