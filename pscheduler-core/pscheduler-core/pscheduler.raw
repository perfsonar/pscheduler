#!/bin/sh -e
#
# pscheduler - Front-end CLI program for pScheduler
#

WHOAMI=$(basename $0)

die()
{
    [ "$@" ] && echo "$@" 1>&2
    exit 1
}


help()
{
    echo "Usage: ${WHOAMI} command [ arguments ]"
    echo
    echo "Commands:  (Use 'command --help' for further help.)"
    echo
    ls "__COMMANDS__" \
	| fgrep -xv internal \
	| pr -4 -T -t \
	| sed -e 's/^/    /g'
    echo
}


if [ $# -lt 1 ]
then
    help 1>&2
    die
fi

COMMAND="$1"
shift

case "${COMMAND}" in
    
    --help|-h|help)
	help
	exit 0
	;;

    --*)
	die "Unknown option ${COMMAND}.  Use --help for help."
	exit 1
	;;

    *)
	RUN="__COMMANDS__/${COMMAND}"

	[ -x "${RUN}" ] \
	    || die "${COMMAND}: Unknown command.  Use --help for help."

	exec "${RUN}" "$@"
	;;

esac

die "Internal error:  this should not be reached."
