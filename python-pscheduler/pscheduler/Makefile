#
# Makefile for python-pscheduler module
#

default: build test

build:
	python setup.py build

# This is disabled because the test suite works differently on CentOS
# 6 and 7.
test:
	nosetests ./tests


clean:
	rm -rf build
	find pscheduler -name "*.pyc" | xargs rm -rf
	find . -name "*~" | xargs rm -rf
