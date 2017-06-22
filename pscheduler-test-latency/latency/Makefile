#
# Makefile for any test class
#

NAME=latency

FILES=\
	cli-to-spec \
	enumerate \
	limit-is-valid \
	limit-passes \
	participants \
	pscheduler-schema-latency-request.json \
	pscheduler-schema-latency-response.json \
	result-format \
	spec-format \
	spec-is-valid \
	spec-to-cli \

MODULES=\
	latency_utils \
	validate \

PYS=$(MODULES:%=%.py)
PYCS=$(MODULES:%=%.pyc)

$(PYCS):
	python -m compileall .
TO_CLEAN += $(PYCS)



install: $(FILES) $(PYS) $(PYCS)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)
	install -m 444 $(PYS) $(PYCS) $(DESTDIR)


clean:
	rm -f $(TO_CLEAN) *~
