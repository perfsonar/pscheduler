#
# Makefile for pScheduler API Server
#

NAME=pscheduler-api-server

# Root python module, which is a stripped name.
MODULE=$(shell echo "$(NAME)" | tr -c -d 'A-Za-z0-9')

default: build


%: %.m4
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
	m4 \
		"-D__NAME__=$(NAME)" \
		"-D__MODULE__=$(MODULE)" \
		"-D__USER_NAME__=$(USER_NAME)" \
		"-D__GROUP_NAME__=$(GROUP_NAME)" \
		"-D__API_ROOT__=$(API_ROOT)" \
		"-D__API_DIR__=$(API_DIR)" \
		"-D__DSN_FILE__=$(DSN_FILE)" \
		"-D__LIMITS_FILE__=$(LIMITS_FILE)" \
		< $^ > $@
	@if egrep -e '__[A-Z_]+__' $@ ; then \
		echo "Found un-substituted values in processed file $@" ; \
		false ; \
	fi


CONFIG=$(NAME).conf
WSGI=$(NAME).wsgi

build: $(CONFIG) $(WSGI) pschedulerapiserver/__init__.py
	python -m compileall .
TO_CLEAN += $(CONFIG) $(WSGI) *.pyc

install: build
ifndef CONF_D
	@echo No CONF_D specified for build
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

