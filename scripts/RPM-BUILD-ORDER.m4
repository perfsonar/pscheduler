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
# RPM BUILD UTILITIES
#
# Everything else depends on these.
#
rpm-with-deps
make-generic-rpm

#
# DEVELOPMENT, LIBRARIES AND UTILITIES
#

# PostgreSQL Additions
postgresql-init
postgresql-load

# Python Modules
python-argparse
ifelse(REDHAT_RELEASE_MAJOR,7,
    python-functools32,)
python-isodate
python-netaddr
python-ntplib
python-py-radix
# TODO: This can be dropped in 1.2
python-repoze.lru
python-subprocess32
python-tzlocal
python-vcversioner

# JSON Tools
# Available as python2-jsonschema in EPEL for EL7
ifelse(REDHAT_RELEASE_MAJOR,6,python-jsonschema,)
ifelse(REDHAT_RELEASE_MAJOR,6,python-jsontemplate,)


# Home-grown Python Modules
python-icmperror

# Apache add-ons
httpd-firewall
httpd-wsgi-socket


#
# Utility and Tool programs
#
drop-in
# JQ was used in development but isn't needed for production.
#jq
paris-traceroute
random-string


#
# PSCHEDULER CORE PARTS
#

pscheduler-rpm
pscheduler-account
python-pscheduler
pscheduler-core
pscheduler-server

#
# PSCHEDULER PLUG-INS
#

# Tests
pscheduler-test-clock
pscheduler-test-idle
pscheduler-test-idlebgm
pscheduler-test-idleex
pscheduler-test-latency
pscheduler-test-latencybg
pscheduler-test-throughput
pscheduler-test-rtt
pscheduler-test-simplestream
pscheduler-test-trace
pscheduler-test-dns

# Tools
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
pscheduler-tool-simplestreamer
pscheduler-tool-sleep
pscheduler-tool-sleepbgm
pscheduler-tool-snooze
pscheduler-tool-ping
pscheduler-tool-psclock
pscheduler-tool-tracepath
pscheduler-tool-traceroute
pscheduler-tool-paris-traceroute
pscheduler-tool-dnspy

# Archivers
pscheduler-archiver-bitbucket
pscheduler-archiver-esmond
pscheduler-archiver-failer
pscheduler-archiver-http
pscheduler-archiver-rabbitmq
pscheduler-archiver-syslog

# Misc.
pscheduler-docs


# Bundles
pscheduler-bundle-full
