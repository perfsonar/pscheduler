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
pgdg-srpm-macros
postgresql
postgresql-init
postgresql-load


# Only build this on OL8.  EL8 has it.
ifelse(REDHAT_RELEASE_MAJOR,8,ifelse(VENDOR,oracle,oniguruma))
# jq version with new patches. replace when patches accepted upstream
jq

# Python Modules
# Only build this on OL8.  EL8 has it.
ifelse(REDHAT_RELEASE_MAJOR,8,ifelse(VENDOR,oracle,Cython))
ifelse(REDHAT_RELEASE_MAJOR,7,python-daemon)
ifelse(REDHAT_RELEASE_MAJOR,7,python-isodate)
# EL8 has this, but an older version
python-itsdangerous
python-pyrsistent
# EL8 has this, but an older version
python-jsonschema
python-kafka

# Used by pscheduler-archiver-esmond

# EL8's is 1.58, ours is/was 1.59.  Commits to the project show only
# cosmetic changes for the later version.
ifelse(REDHAT_RELEASE_MAJOR,7,python-memcached)

# EL8 has this, ours is newer
python-netifaces
ifelse(REDHAT_RELEASE_MAJOR,7,python-ntplib)
python-parse-crontab
python-vine
python-py-amqp
python-py-radix
python-pyjq
python-tzlocal
python-vcversioner
# EL8 has this, ours is newer
python-pyasn1
python-pyasn1-modules
# EL8 has this, ours is newer
python-werkzeug
# EL8 has this, ours is newer
python-flask
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
ethr
# TODO: Building temporarily for EL8; required for owamp
ifelse(REDHAT_RELEASE_MAJOR,8,I2util)
# EPEL dropped this for EL8
ifelse(REDHAT_RELEASE_MAJOR,8,iperf)
# TODO: Building temporarily for EL8
ifelse(REDHAT_RELEASE_MAJOR,8,owamp)
paris-traceroute
random-string
s3-benchmark

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
pscheduler-test-latency
pscheduler-test-latencybg
pscheduler-test-netreach			--bundle extras
pscheduler-test-throughput
pscheduler-test-rtt
pscheduler-test-s3throughput
pscheduler-test-simplestream
pscheduler-test-snmpget			--bundle snmp
pscheduler-test-snmpgetbgm		--bundle snmp
pscheduler-test-snmpset			--bundle snmp
pscheduler-test-trace
pscheduler-test-dns

# Tools
pscheduler-tool-bwctliperf2		--bundle obsolete
pscheduler-tool-bwctliperf3		--bundle obsolete
pscheduler-tool-bwctlping		--bundle obsolete
pscheduler-tool-bwctltracepath		--bundle obsolete
pscheduler-tool-bwctltraceroute		--bundle obsolete
pscheduler-tool-curl
pscheduler-tool-dnspy
pscheduler-tool-ethr
pscheduler-tool-globus			--bundle extras
pscheduler-tool-iperf2
pscheduler-tool-iperf3
pscheduler-tool-net-snmp-set		--bundle snmp
pscheduler-tool-nmapreach			--bundle extras
pscheduler-tool-nuttcp
pscheduler-tool-owping
pscheduler-tool-paris-traceroute
pscheduler-tool-ping
pscheduler-tool-powstream
pscheduler-tool-psclock
pscheduler-tool-psurl			--bundle obsolete
pscheduler-tool-pysnmp			--bundle snmp
pscheduler-tool-s3-benchmark
pscheduler-tool-simplestreamer
pscheduler-tool-sleep
pscheduler-tool-sleepbgm
pscheduler-tool-snooze
pscheduler-tool-tracepath
pscheduler-tool-traceroute
pscheduler-tool-twping

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
