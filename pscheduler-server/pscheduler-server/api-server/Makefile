#
# Makefile for pScheduler API Server
#

NAME=pscheduler-api-server

# Root python module, which is a stripped name.
MODULE=$(shell echo "$(NAME)" | tr -c -d 'A-Za-z0-9')

default: build


%: %.raw
ifndef USER_NAME
	@echo No USER_NAME specified for build
	@false
endif
ifndef GROUP_NAME
	@echo No GROUP_NAME specified for build
	@false
endif
ifndef API_ROOT
	@echo No API_ROOT specified for build
	@false
endif
ifndef API_DIR
	@echo No API_DIR specified for build
	@false
endif
ifndef DSN_FILE
	@echo No DSN_FILE specified for build
	@false
endif
ifndef LIMITS_FILE
	@echo No LIMITS_FILE specified for build
	@false
endif
ifndef RUN_DIR
	@echo No RUN_DIR specified for build
	@false
endif
	sed \
		-e 's|__NAME__|$(NAME)|g' \
		-e 's|__MODULE__|$(MODULE)|g' \
		-e 's|__USER_NAME__|$(USER_NAME)|g' \
		-e 's|__GROUP_NAME__|$(GROUP_NAME)|g' \
		-e 's|__API_ROOT__|$(API_ROOT)|g' \
		-e 's|__API_DIR__|$(API_DIR)|g' \
		-e 's|__DSN_FILE__|$(DSN_FILE)|g' \
		-e 's|__LIMITS_FILE__|$(LIMITS_FILE)|g' \
		-e 's|__RUN_DIR__|$(RUN_DIR)|g' \
		< $^ > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi


CONFIG=$(NAME).conf
WSGI=$(NAME).wsgi

RAWS=$(wildcard pschedulerapiserver/*.raw)
UNRAWS=$(basename $(RAWS))

build: $(CONFIG) $(WSGI) $(UNRAWS)
	python -m compileall .
TO_CLEAN += $(CONFIG) $(WSGI) *.pyc

install: build
ifndef CONF_D
	@echo No CONF_D specified for $@
	@false
endif
	mkdir -p $(PREFIX)/$(CONF_D)
	install -m 444 $(CONFIG) $(PREFIX)/$(CONF_D)
	mkdir -p $(PREFIX)/$(API_DIR)
	install -m 444 *.pyc *.wsgi $(PREFIX)/$(API_DIR)
	mkdir -p $(PREFIX)/$(API_DIR)/pschedulerapiserver
	install -m 444 pschedulerapiserver/*.pyc $(PREFIX)/$(API_DIR)/pschedulerapiserver




clean:
	rm -rf $(TO_CLEAN) *~
	make -C pschedulerapiserver $@

