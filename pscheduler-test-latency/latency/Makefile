#
# Makefile for any test class
#

NAME=latency

FILES=\
	cli-to-spec \
	enumerate \
	latency_utils.py \
	participants \
	pscheduler-schema-latency-request.json \
	pscheduler-schema-latency-response.json \
	result-format \
	spec-format \
	spec-is-valid \
	spec-to-cli \


DOCS=\
	$(NAME).txt



install: $(FILES) $(DOCS)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
ifdef DOCS
ifndef DOCDIR
	@echo No DOCDIR specified for installation
	@false
endif
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)
ifdef DOCS
	mkdir -p $(DOCDIR)
	install -m 444 $(DOCS) $(DOCDIR)
endif



clean:
	rm -f $(TO_CLEAN) *~
