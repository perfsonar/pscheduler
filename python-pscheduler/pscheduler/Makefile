#
# Makefile for python-pscheduler module
#

default: build


test:
	nosetests

test-coverage:
	nosetests --with-coverage --cover-package rabbitmq


build:
	python setup.py build

clean:
	make -C tests $@
