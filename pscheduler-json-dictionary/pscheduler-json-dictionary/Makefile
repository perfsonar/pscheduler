#
# Makefile for pScheduler JSON Dictionary
#

NAME := json-dictionary

default: build

JSON := $(NAME).json
PICKLED := $(NAME).pickled
TO_CLEAN += $(PICKLED)


PICKLER := ./pickle-json
%.pickled: %.json $(PICKLER)
	$(PICKLER) < $< > $@

INTERNAL := json-dictionary
$(INTERNAL): $(INTERNAL).raw
ifndef DATADIR
	@echo No DATADIR specified for build
	@false
endif
	sed -e "s|__DATADIR__|$(DATADIR)|g" < $< > $@
TO_CLEAN += $(INTERNAL)


TESTS := ./tests
test: $(JSON) $(TESTS)
	./run-tests --prefix pScheduler "$(JSON)" "$(TESTS)"


build: test $(PICKLED) $(INTERNAL)



install: $(PICKLED) $(INTERNAL)
ifndef INTERNALSDIR
	@echo No INTERNALSDIR specified for installation
	@false
endif
ifndef INSTALLED_DATADIR
	@echo No INSTALLED_DATADIR specified for installation
	@false
endif
	mkdir -p $(INTERNALSDIR)
	install -m 555 $(INTERNAL) $(INTERNALSDIR)
	mkdir -p $(INSTALLED_DATADIR)
	install -m 444 $(JSON) $(INSTALLED_DATADIR)
	install -m 444 $(PICKLED) $(INSTALLED_DATADIR)


clean:
	rm -f $(TO_CLEAN)
	find . -name "*~" | xargs rm -rf
