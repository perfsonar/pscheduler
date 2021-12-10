#
# Makefile for limit examples
#

FILES := \
	$(wildcard classification-*) \
	$(wildcard general-*) \
	$(wildcard identifier-*)

default: validate


%-check: %
	pscheduler validate-limits --quiet $<

validate: $(FILES:%=%-check)


clean:
	rm -rf $(TO_CLEAN) *~
