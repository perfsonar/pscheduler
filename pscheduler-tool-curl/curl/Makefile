#
# Makefile for any tool class
#

NAME := curl

PROGRAMS := \
	can-run \
	duration \
	enumerate \
	merged-results \
	participant-data \
	run

MODULES :=  run_http

PYS := $(MODULES:%=%.py)
PYCACHE := __pycache__
$(PYCACHE): $(PYS)
ifndef PYTHON
	@echo No PYTHON specified for build
	@false
endif
	$(PYTHON) -m compileall .
TO_CLEAN += $(PYCACHE)

FILES := $(PROGRAMS) $(PYS)


install: $(FILES) $(PYCACHE)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false

endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)
	cp -r $(PYCACHE) $(DESTDIR)

clean:
	rm -rf $(TO_CLEAN) *~
