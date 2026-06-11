#
# Makefile for enumerations
#

FILES := \
	tests \
	tools \
	archivers \
	contexts

JSONS := $(FILES:%=%.json)

DATA := data.json

TARBALL := pscheduler-enumeration-$(shell date +%Y%m%d%H%M%S).tar

APP_DIR := app
APP := enumerator

default: $(APP)


prep:
	sudo dnf -y install python3-pip zip jq


%.json: .FORCE
	curl -sk 'https://localhost/pscheduler/$(basename $@)?expanded&pretty' > "$@"
TO_CLEAN += $(JSONS)


# JSON file containing all of the enumeration files as a hash
DATA_BUILD := data-build.json
DATA_BUILD_OUT := data-build-out.json
$(DATA): $(JSONS)
	rm -f $(DATA_BUILD)
	echo '{}' > $(DATA_BUILD)
	for JSON in $^ ; \
	do \
		NAME=$$(basename "$${JSON}" | sed -e 's/\..*$$//g') ; \
		jq --arg name $$NAME --slurp '.[0][$$name] = .[1] | .[0]' \
			$(DATA_BUILD) "$${NAME}.json" > $(DATA_BUILD_OUT) ; \
		mv $(DATA_BUILD_OUT) $(DATA_BUILD) ; \
	done
	mv $(DATA_BUILD) $@
TO_CLEAN += $(DATA) $(DATA_BUILD) $(DATA_BUILD_OUT)


# Python module containing all of the data as a JSON-loaded string
DATA_PY := data.py
$(DATA_PY): $(DATA)
	echo '# This file is built.  DO NOT EDIT.' > $@
	echo 'import json' >> $@
	echo "data = json.loads('''" >> $@
	sed -e 's/\\/\\\\/g' $< >> $@
	echo "''')" >> $@
TO_CLEAN += $(DATA_PY)


# Build-up of app directory
BUILD := ./$(APP)-build
$(BUILD): $(PREP) $(DATA_PY) .FORCE
	rm -rf $@
	mkdir -p $@
	cp -r $(APP_DIR)/* $@
	cp $(DATA_PY) $@/enumerator
	(cd $(BUILD) && pip3 install flask --target ./)
TO_CLEAN += $(BUILD)


APP_ZIP := $(APP).zip
$(APP_ZIP): $(BUILD)
	(cd $(BUILD) && zip -r - . -x '*~') > $@
TO_CLEAN += $(APP_ZIP)


# Zip of app turned into a runnable Python program
$(APP): $(APP_ZIP)
	echo '#!/usr/bin/env python3' | cat - $(APP_ZIP) > $@
	chmod +x $@
TO_CLEAN += $(APP)


run: $(APP)
	PATH=.:$(PATH) $(APP)


.FORCE::


$(TARBALL): $(JSONS) README.md
	tar cf "$@" $^
TO_CLEAN += pscheduler-enumeration-*.tar


build: $(APP)


clean:
	rm -rf $(TO_CLEAN)
	find . -name '*~' | xargs rm -rf
