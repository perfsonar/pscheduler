#
# Makefile for python-pscheduler module
#

default: build


file-setup:
ifndef CLASSES
	@echo No CLASSES specified for build
	@false
endif
	find pscheduler -type f -name "*.py" \
	| xargs sed -i -e 's|__CLASSES__|$(CLASSES)|'


test: file-setup
	python3 -m nose

test-coverage: file-setup
	python3 -m nose --with-coverage --cover-package rabbitmq


build: file-setup test
	python3 setup.py build

clean:
	make -C tests $@
	find . -name "*.pyc" | xargs rm -f
