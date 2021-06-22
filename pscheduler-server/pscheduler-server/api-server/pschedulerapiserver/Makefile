#
# Makefile for pschedulerapiserver
#

default: build


TO_CLEAN += *.pyc

RAWS := $(wildcard *.raw)
PROCESSED := $(basename $(RAWS))


%: %.raw
ifndef RUN_DIR
	@echo RUN_DIR not defined for $@
	false
endif
	sed \
		-e 's|__RUN_DIR__|$(RUN_DIR)|g' \
		< $< > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi


build:
	echo $(PROCESSED)
TO_CLEAN += $(PROCESSED)

clean:
	rm -rf $(TO_CLEAN) *~
