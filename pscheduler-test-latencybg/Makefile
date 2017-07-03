#
# Makefile for Python pScheduler Latency Test Class
#

AUTO_TARBALL=1

include make/generic-rpm.make

test::
	nosetests

test-coverage::
	nosetests --with-coverage --cover-package latency
