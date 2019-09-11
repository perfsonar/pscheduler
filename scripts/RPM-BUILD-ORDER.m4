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

# PostgreSQL and Additions

# Neither EL7 nor PGDG's distro provide PL/Python3.  This will build
# it if EPEL is present.
ifelse(REDHAT_RELEASE_MAJOR,7,postgresql)
postgresql-init
postgresql-load

# jq version with new patches. replace when patches accepted upstream
jq

# Python Modules
python-daemon
python-isodate
python-itsdangerous
python-pyrsistent
python-jsonschema
python-kafka
# Used by pscheduler-archiver-esmond
python-memcached
python-netifaces
python-ntplib
python-parse-crontab
python-py-radix
python-pyjq
### # TODO: This can be dropped in 1.2
### # TODO: See if the above is actually true.  May have been for Flask?
### python-repoze.lru
python-tzlocal
python-vcversioner
python-pyasn1
python-pyasn1-modules
python-werkzeug
python-flask
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
pscheduler-test-disk-to-disk		--bundle extras
pscheduler-test-http
pscheduler-test-idle
pscheduler-test-idlebgm
pscheduler-test-idleex
### pscheduler-test-latency
### pscheduler-test-latencybg
pscheduler-test-netreach			--bundle extras
### pscheduler-test-throughput
pscheduler-test-rtt
pscheduler-test-simplestream
### pscheduler-test-snmpget			--bundle snmp
### pscheduler-test-snmpgetbgm		--bundle snmp
### pscheduler-test-snmpset			--bundle snmp
pscheduler-test-trace
pscheduler-test-dns

# Tools
pscheduler-tool-bwctliperf2		--bundle obsolete
pscheduler-tool-bwctliperf3		--bundle obsolete
pscheduler-tool-bwctlping		--bundle obsolete
pscheduler-tool-bwctltracepath		--bundle obsolete
pscheduler-tool-bwctltraceroute		--bundle obsolete
pscheduler-tool-curl			--bundle extras
pscheduler-tool-dnspy
pscheduler-tool-globus			--bundle extras
### pscheduler-tool-iperf2
### pscheduler-tool-iperf3
### pscheduler-tool-net-snmp-set		--bundle snmp
pscheduler-tool-nmapreach			--bundle extras
### pscheduler-tool-nuttcp
### pscheduler-tool-owping
pscheduler-tool-paris-traceroute
pscheduler-tool-ping
### pscheduler-tool-powstream
pscheduler-tool-psclock
pscheduler-tool-psurl
### pscheduler-tool-pysnmp			--bundle snmp
pscheduler-tool-simplestreamer
pscheduler-tool-sleep
pscheduler-tool-sleepbgm
pscheduler-tool-snooze
pscheduler-tool-tracepath
pscheduler-tool-traceroute
### pscheduler-tool-twping
### 
# Archivers
pscheduler-archiver-bitbucket
pscheduler-archiver-esmond
pscheduler-archiver-failer
pscheduler-archiver-http
pscheduler-archiver-kafka
pscheduler-archiver-rabbitmq
pscheduler-archiver-snmptrap		--bundle snmp
pscheduler-archiver-syslog

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
