#
# Makefile for any archiver class
#

NAME=rabbitmq

# TODO: This should be an includable template.

FILES=\
	enumerate \
	data-is-valid \
	archive

default:
	@echo "No default target."


# ------------------------------------------------------------------------------

# Local copy of python-pika 0.10.0
#
# This is required because the version provided by EPEL on EL6 doesn't
# have the URLParameters class.
#
# TODO: Remove after we drop support for EL6.
# TODOL Also remove $(MAKE) pika-install in install target.

PIKA_VERSION=0.10.0
PIKA_DIR=pika-$(PIKA_VERSION)
PIKA_TARBALL=$(PIKA_DIR).tar.gz

pika: $(PIKA_TARBALL)
	rm -rf $@
	zcat $< | tar xf -
	cd $(PIKA_DIR) && python setup.py build
	cd $(PIKA_DIR) && python -m compileall .
	cp -r $(PIKA_DIR)/pika $@
TO_CLEAN += $(PIKA_DIR) pika

pika-install: pika
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	cp -r $< $(DESTDIR)
	find $(DESTDIR) -name "*.py*" | xargs chmod 444

#
# End of pika
#
# ------------------------------------------------------------------------------


install: $(FILES)
ifndef DESTDIR
	@echo No DESTDIR specified for installation
	@false
endif
	mkdir -p $(DESTDIR)
	install -m 555 $(FILES) $(DESTDIR)
	$(MAKE) pika-install



clean:
	rm -rf $(TO_CLEAN) *~
