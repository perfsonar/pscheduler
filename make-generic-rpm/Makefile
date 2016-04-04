#
# Make-generic-rpm Makefile, Stage 1
#

default: build



%:
	which spectool 2>&1 > /dev/null || yum -y install spectool
	which rpmbuild 2>&1 > /dev/null || yum -y install rpm-build
	$(MAKE) -f Makefile-stage2 $@
