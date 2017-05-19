#
# Makefile for python-pscheduler module
#

default: build test

build:
	python setup.py build

test:
	nosetests ./tests


clean:
	rm -rf build
	find pscheduler -name "*.pyc" | xargs rm -rf
	find . -name "*~" | xargs rm -rf
