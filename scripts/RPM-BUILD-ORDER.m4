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

# System Setup
rsyslog-debug

# PostgreSQL Additions
postgresql-init
postgresql-load

# Python Modules
python-argparse
python-detach
python-dnspython
ifelse(REDHAT_RELEASE_MAJOR,7,
    python-functools32,)
python-isodate
python-netaddr
python-ntplib
python-py-radix
python-pytz
python-repoze.lru
python-subprocess32
python-tzlocal
python-vcversioner

# JSON Tools
python-jsonschema
python-jsontemplate

# Flask and its dependencies
python-itsdangerous
python-Jinja2
python-Werkzeug
python-Flask

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


#
# PSCHEDULER PLUG-INS
#

# Tests
pscheduler-test-idle
pscheduler-test-latency
pscheduler-test-throughput
pscheduler-test-rtt
pscheduler-test-simplestream
pscheduler-test-trace

# Tools
# TODO: This has dependencies outside the local tree.
pscheduler-tool-owping
pscheduler-tool-iperf
pscheduler-tool-simplestreamer
pscheduler-tool-sleep
pscheduler-tool-snooze
pscheduler-tool-ping
pscheduler-tool-tracepath
pscheduler-tool-traceroute
pscheduler-tool-paris-traceroute

# Archivers
pscheduler-archiver-bitbucket
pscheduler-archiver-failer
pscheduler-archiver-syslog


# Servers
pscheduler-database
pscheduler-server
pscheduler-api-server
