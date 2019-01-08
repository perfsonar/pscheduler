#
# Make-generic-rpm Makefile, Stage 1
#

default: build



%:
	which spectool > /dev/null 2>&1 || yum -y install spectool
	which rpmbuild > /dev/null 2>&1 || yum -y install rpm-build
	$(MAKE) -f Makefile-stage2 $@
