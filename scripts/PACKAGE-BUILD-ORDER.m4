dnl
dnl Build Order for pScheduler RPMs
dnl
dnl
dnl Pre-process with M4.
dnl
changequote(<!,!>)dnl
changecom()dnl
dnl
#
# Packages must be listed in an order where dependent packages are
# built after their dependencies.
#
#
# Options that can be added to a package line:
#
#  --bundle b   Include the package in bundle b and not the default
#               full bundle.
#
# The following macros are provided to use in determining whether or
# not to build a package:
#
# OS         Operating system, per 'uname -s'       Linux, Darwin
# FAMILY     OS family, empty if not applicable     RedHat, Debian
# DISTRO     OS distribution (LSB ID)               RHEL, CentOS, Oracle, Debian, Ubuntu
# RELEASE    Distribution release                   7.8.2003
# MAJOR      Major part of RELEASE                  7
# MINOR      Minor part of RELEASE                  8
# ARCH       System architecture, per 'uname -m'    x86_64, armhf
# PACKAGING  Type of packaging on this system       rpm, deb
#
#
# Note that there is no need to make decisions for RPM- or Debian-only
# builds in this file; if there is no packaging information for an OS
# family in with the sources, it will not be built.
#


# GENERAL-PURPOSE MACROS

# Debian 9 doesn't support Golang sufficiently for what we need, nor
# is there support for it on arm64 or ppc64el.
# TODO: Doesn't build properly anywhere on Debian.
# TODO: Antoine says this is okay on Deb10
define(HAVE_GOLANG,ifelse(FAMILY/MAJOR,Debian/9,,
              FAMILY/ARCH,Debian/arm64,,
              FAMILY/ARCH,Debian/ppc64el,,
              1))


#
# PACKAGE BUILD UTILITIES
#
# Everything else depends on these.
#
ifelse(PACKAGING,rpm,rpm-with-deps)
make-generic-package

# Build this early.  Some of the packages using PostgreSQL depend on
# knowing what version is required to avoid the "Requires: postgresql"
# trap we fell into with RH6.
ifelse(PACKAGING,rpm,pscheduler-rpm)

#
# DEVELOPMENT, LIBRARIES AND UTILITIES
#

# PostgreSQL and Additions
pgdg-srpm-macros
postgresql
postgresql-init
postgresql-load

ifelse(DISTRO/MAJOR,Oracle/8,oniguruma)			# Only build this on OL8.  CentOS 7 and EL8 have it.

# Our version of jq has patches. replace when patches accepted upstream.
jq

# Python Modules

ifelse(FAMILY/DISTRO/MAJOR,RedHat/Oracle/8,Cython)	# Only build this on OL8.
ifelse(FAMILY/MAJOR,Debian/9,python-attrs)              # Needed here only.
ifelse(FAMILY/MAJOR,RedHat/7,python-daemon)		# EL7 needs this; EL8 is up to date
ifelse(FAMILY/MAJOR,RedHat/7,python-isodate)		# EL7 needs this; EL8 is up to date
ifelse(FAMILY/MAJOR,RedHat/8,python-itsdangerous)	# EL8 has this, but an older version
python-pyrsistent
python-nmap3
# EL8 has this, but an older version
python-jsonschema
python-kafka
python-nmap3

# Used by pscheduler-archiver-esmond
# EL8's is 1.58, ours is/was 1.59.  Commits to the project show only
# cosmetic changes for the later version.
ifelse(DISTRO/MAJOR,CentOS/7,python-memcached)

python-netifaces
ifelse(DISTRO/MAJOR,CentOS/7,python-ntplib)		# EL8 has this, ours is newer
python-parse-crontab
python-vine
python-py-amqp
python-py-radix
python-pyjq
python-tzlocal
python-vcversioner
python-pyasn1						# EL8 has this, ours is newer
python-pyasn1-modules
python-werkzeug						# EL8 has this, ours is newer
python-flask						# EL8 has this, ours is newer

# TODO: EPEL8 has a newer version that doesn't install.
# See https://bugzilla.redhat.com/show_bug.cgi?id=1838402
python-pysnmp

# JSON Tools
python-jsontemplate


# Home-grown Python Modules
python-icmperror


# Apache add-ons
httpd-firewall
mod_wsgi
httpd-wsgi-socket


#
# Utility and Tool programs
#
drop-in

ifelse(HAVE_GOLANG,1,ethr)
ifelse(FAMILY/MAJOR,REDHAT/8,I2util)			# TODO: Building temporarily for EL8; required for owamp
ifelse(FAMILY/MAJOR,REDHAT/8,iperf)			# EPEL dropped this for EL8
ifelse(FAMILY/MAJOR,REDHAT/8,owamp)			# TODO: Building temporarily for EL8
paris-traceroute
random-string
<<<<<<< HEAD:scripts/PACKAGE-BUILD-ORDER.m4
ifelse(HAVE_GOLANG,1,s3-benchmark)
=======
s3-benchmark
tcpping

>>>>>>> 5.0.0:scripts/RPM-BUILD-ORDER.m4

#
# PSCHEDULER CORE PARTS
#

pscheduler-account
pscheduler-jq-library
python-pscheduler
pscheduler-core
pscheduler-server

#
# PSCHEDULER PLUG-INS
#

# Tests
pscheduler-test-clock
pscheduler-test-dhcp			--bundle extras
pscheduler-test-disk-to-disk		--bundle extras
pscheduler-test-dot1x			--bundle extras
pscheduler-test-http
pscheduler-test-idle
pscheduler-test-idlebgm
pscheduler-test-idleex
pscheduler-test-latency
pscheduler-test-latencybg
<<<<<<< HEAD:scripts/PACKAGE-BUILD-ORDER.m4
pscheduler-test-netreach		--bundle extras
=======
pscheduler-test-netreach			--bundle extras
pscheduler-test-psresponse
>>>>>>> 5.0.0:scripts/RPM-BUILD-ORDER.m4
pscheduler-test-throughput
pscheduler-test-openports		--bundle extras
pscheduler-test-rtt
ifelse(HAVE_GOLANG,1,pscheduler-test-s3throughput)
pscheduler-test-simplestream
pscheduler-test-snmpget			--bundle snmp
pscheduler-test-snmpgetbgm		--bundle snmp
pscheduler-test-snmpset			--bundle snmp
pscheduler-test-trace
pscheduler-test-dns
pscheduler-test-mtu
pscheduler-test-wifibssid


# Tools
pscheduler-tool-bssidscanner
pscheduler-tool-bwctliperf2		--bundle obsolete
pscheduler-tool-bwctliperf3		--bundle obsolete
pscheduler-tool-bwctlping		--bundle obsolete
pscheduler-tool-bwctltracepath		--bundle obsolete
pscheduler-tool-bwctltraceroute		--bundle obsolete
pscheduler-tool-curl
pscheduler-tool-dhclient		--bundle extras
pscheduler-tool-dnspy
<<<<<<< HEAD:scripts/PACKAGE-BUILD-ORDER.m4

ifelse(HAVE_GOLANG,1,pscheduler-tool-ethr)
=======
pscheduler-tool-ethr
pscheduler-tool-fpingreach		--bundle extras
pscheduler-tool-fwmtu
>>>>>>> 5.0.0:scripts/RPM-BUILD-ORDER.m4
pscheduler-tool-globus			--bundle extras
pscheduler-tool-halfping
pscheduler-tool-iperf2
pscheduler-tool-iperf3
pscheduler-tool-net-snmp-set		--bundle snmp
<<<<<<< HEAD:scripts/PACKAGE-BUILD-ORDER.m4
pscheduler-tool-nmapreach		--bundle extras
=======
pscheduler-tool-nmapreach			--bundle extras
pscheduler-tool-nmapscan		--bundle extras
>>>>>>> 5.0.0:scripts/RPM-BUILD-ORDER.m4
pscheduler-tool-nuttcp
pscheduler-tool-owping
pscheduler-tool-paris-traceroute
pscheduler-tool-ping
pscheduler-tool-powstream
pscheduler-tool-psclock
pscheduler-tool-pstimer
pscheduler-tool-psurl			--bundle obsolete
pscheduler-tool-pysnmp			--bundle snmp
ifelse(HAVE_GOLANG,1,pscheduler-tool-s3-benchmark)
pscheduler-tool-simplestreamer
pscheduler-tool-sleep
pscheduler-tool-sleepbgm
pscheduler-tool-snooze
pscheduler-tool-tcpping
pscheduler-tool-tracepath
pscheduler-tool-traceroute
pscheduler-tool-twping
pscheduler-tool-umichwpa		--bundle extras

# Archivers
pscheduler-archiver-bitbucket
pscheduler-archiver-esmond
pscheduler-archiver-failer
pscheduler-archiver-http
pscheduler-archiver-kafka
pscheduler-archiver-postgresql
pscheduler-archiver-rabbitmq
pscheduler-archiver-snmptrap		--bundle snmp
pscheduler-archiver-syslog
pscheduler-archiver-tcp
pscheduler-archiver-udp

# Context Changers
pscheduler-context-changefail
pscheduler-context-changenothing
pscheduler-context-linuxnns
pscheduler-context-linuxvrf


# Misc.
pscheduler-docs


# Bundles
pscheduler-bundle-extras
pscheduler-bundle-full
pscheduler-bundle-obsolete
pscheduler-bundle-snmp
