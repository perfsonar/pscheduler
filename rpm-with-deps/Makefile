#
# Makefile for rpm-with-deps RPM
#
# This package is built by hand because make-generic-package depends
# on it (RedHat-derived systems only).
#


NAME=$(shell fgrep Name: *.spec | awk '{ print $$2 }')
VERSION=$(shell fgrep Version: *.spec | awk '{ print $$2 }')

RPMDIR=$(shell pwd)/BUILD
BUILDROOT=$(RPMDIR)/BUILDROOT


default: build


.rpmmacros:
	rm -f $@
	echo %_topdir $(RPMDIR) > .rpmmacros
TO_CLEAN += .rpmmacros


FULLNAME=$(NAME)-$(VERSION)
TARBALL=$(FULLNAME).tar.gz

$(TARBALL):
	rm -f $@ $(FULLNAME)
	cp -r $(NAME) $(FULLNAME)
	tar czf $@ $(NAME) $(FULLNAME)
	rm -rf $(FULLNAME)
TO_CLEAN += $(TARBALL) $(FULLNAME)


$(RPMDIR): $(TARBALL)
	rpm -q rpm-build || yum -y install rpm-build
	mkdir -p \
		$(RPMDIR)/BUILD \
		$(RPMDIR)/RPMS \
		$(RPMDIR)/SOURCES \
		$(RPMDIR)/SPECS \
		$(RPMDIR)/SRPMS \
		$(BUILDROOT)
	cp -pf $(TARBALL) $(RPMDIR)/SOURCES
	cp -pf $(NAME).spec $(RPMDIR)/SPECS
TO_CLEAN += $(RPMDIR) $(BUILDROOT)

LOG=LOG
build: .rpmmacros $(TARBALL) $(RPMDIR)
	HOME=$(shell pwd) rpmbuild -v -ba --buildroot $(BUILDROOT) ./$(NAME).spec 2>&1 \
                | tee $(LOG)
TO_CLEAN += $(LOG)


srpm: .rpmmacros $(TARBALL) $(RPMDIR)
	HOME=$(shell pwd) rpmbuild -v -bs --buildroot $(BUILDROOT) ./$(NAME).spec 2>&1
	rm -f *.src.rpm
	find $(BUILD_DIR) -name '*.src.rpm' | xargs -I{} cp -pf {} .
TO_CLEAN += *.src.rpm



install: build
	find $(RPMDIR)/RPMS -name "*.rpm" | xargs sudo rpm -Uvh --force


uninstall:
	sudo yum -y remove $(NAME) || true


clean:
	rm -rf $(TO_CLEAN)
	find . -name '*~' | xargs -r rm -f
