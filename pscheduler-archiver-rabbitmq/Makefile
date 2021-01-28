#
# Makefile for Any Archiver
#

AUTO_TARBALL=1

include make/generic-package.make

test::
	nosetests

test-coverage::
	nosetests --with-coverage --cover-package rabbitmq

clean::
	make -C tests $@
