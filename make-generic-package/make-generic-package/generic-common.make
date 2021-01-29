#
# Common Parts of Make Generic Package
#

# Figure out what kind of packages this system runs on

DISTRO_FAMILY := $(shell lsb_release --id --short)

ifeq "$(DISTRO_FAMILY)" ""
$(error "Unable to determine Linux distribution.  (Is lsb_releases installed?)")
endif

ifneq "$(filter CentOS Fedora,$(DISTRO_FAMILY))" ""
PACKAGE_FORMAT := rpm
endif

ifneq "$(filter Debian Ubuntu,$(DISTRO_FAMILY))" ""
PACKAGE_FORMAT := deb
endif

ifeq "$(PACKAGE_FORMAT)" ""
$(error "Don't know how to package for $(DISTRO_FAMILY)")
endif



#
# Convenient shorthands
#

b: build
c: clean
i: install
d: dump
# This is a holdover from the RPM-only days
r: dump

cb: c b
cbd: c b d
cbi: c b i

# CBI with forced clean afterward
cbic: cbi
	$(MAKE) clean

# CBR with forced clean afterward
cbrc cbdc: cbd
	$(MAKE) clean
