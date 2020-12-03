#
# Makefile for a Generic RPM
#

AUTO_TARBALL=1

include make/generic-rpm.make

test::
	nosetests

test-coverage::
	nosetests --with-coverage --cover-package 802.1x
