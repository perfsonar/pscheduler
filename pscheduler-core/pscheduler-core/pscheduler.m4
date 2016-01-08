#!/bin/sh -e
#
# pscheduler - Front-end CLI program for pScheduler
#

WHOAMI=$(basename $0)

die()
{
    echo "$@" 1>&2
    exit 1
}


[ $# -ge 1 ] || die "Usage: ${WHOAMI} command [ arguments ]"

COMMAND=$1
shift

RUN="__COMMANDS__/${COMMAND}"

[ -x "${RUN}" ] || die "${COMMAND}: Unknown command"

exec "${RUN}" "$@"
