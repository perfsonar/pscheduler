dnl
dnl Build Order for pScheduler RPMs
dnl
dnl
dnl Pre-process with M4.
dnl
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


#
# RPM BUILD UTILITIES
#
# Everything else depends on these.
#
rpm-with-deps
make-generic-rpm

# Build this early.  Some of the packages using PostgreSQL depend on
# knowing what version is required to avoid the "Requires: postgresql"
# trap we fell into with RH6.
pscheduler-rpm

#
# DEVELOPMENT, LIBRARIES AND UTILITIES
#

# PostgreSQL Additions
postgresql-init
postgresql-load

# jq version with new patches. replace when patches accepted upstream
jq

# Python Modules
python-setuptools
python-argparse
python-functools32
python-isodate
python2-pyrsistent
python2-jsonschema
python-netaddr
python-ntplib
python-py-radix
python-pyjq
# TODO: This can be dropped in 1.2
python-repoze.lru
python-subprocess32
python-tzlocal
python-vcversioner
# This is how EL prefixes it.
python2-pyasn1
python2-pyasn1-modules
# This doesn't get a python- prefix.  Ask CentOS why.
pysnmp

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
paris-traceroute
random-string


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
pscheduler-test-disk-to-disk	--bundle extras
pscheduler-test-http
pscheduler-test-idle
pscheduler-test-idlebgm
pscheduler-test-idleex
pscheduler-test-latency
pscheduler-test-latencybg
pscheduler-test-netreach
pscheduler-test-throughput
pscheduler-test-rtt
pscheduler-test-simplestream
pscheduler-test-snmpget			--bundle extras
pscheduler-test-snmpgetbgm		--bundle extras
pscheduler-test-snmpset			--bundle extras
pscheduler-test-trace
pscheduler-test-dns
pscheduler-test-disk-to-disk		--bundle extras

# Tools
pscheduler-tool-ftp		            --bundle extras
pscheduler-tool-globus		        --bundle extras
pscheduler-tool-owping
pscheduler-tool-powstream
pscheduler-tool-iperf2
pscheduler-tool-iperf3
pscheduler-tool-nuttcp
pscheduler-tool-bwctliperf2
pscheduler-tool-bwctliperf3
pscheduler-tool-bwctlping
pscheduler-tool-bwctltraceroute
pscheduler-tool-bwctltracepath
pscheduler-tool-net-snmp-set
pscheduler-tool-nmapreach
pscheduler-tool-psurl
pscheduler-tool-pysnmp				--bundle extras
pscheduler-tool-simplestreamer
pscheduler-tool-sleep
pscheduler-tool-sleepbgm
pscheduler-tool-snooze
pscheduler-tool-ping
pscheduler-tool-psclock
pscheduler-tool-tracepath
pscheduler-tool-traceroute
pscheduler-tool-twping
pscheduler-tool-paris-traceroute
pscheduler-tool-dnspy
pscheduler-tool-ftp			--bundle extras
pscheduler-tool-globus			--bundle extras

# Archivers
pscheduler-archiver-bitbucket
pscheduler-archiver-esmond
pscheduler-archiver-failer
pscheduler-archiver-http
pscheduler-archiver-rabbitmq
pscheduler-archiver-snmptrap		--bundle extras
pscheduler-archiver-syslog

# Context Changers
pscheduler-context-changefail
pscheduler-context-changenothing
pscheduler-context-linuxnns
pscheduler-context-linuxvrf


# Misc.
pscheduler-docs


# Bundles
pscheduler-bundle-full
pscheduler-bundle-extras
