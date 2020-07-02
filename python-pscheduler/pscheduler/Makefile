#
# Makefile for python-pscheduler module
#

default: build


test:
	python3 -m nose

test-coverage:
	python3 -m nose --with-coverage --cover-package rabbitmq


build: test
	python3 setup.py build

clean:
	make -C tests $@
	find . -name "*.pyc" | xargs rm -f
