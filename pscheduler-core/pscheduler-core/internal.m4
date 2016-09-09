#!/bin/sh -e

WHOAMI=$(basename "$0")
WHEREAMI=$(dirname "$0")

die()
{
    echo "$@" 1>&2
    exit 1
}

# TODO: Turn on before production
# Keep the uninitiated from running internal commands interactively.
#[ -t 0 -a -t 1 -a -t 2 -a -z "${PERFSONAR_DEVEL}" ] \
#    && die "You probably don't want to do that."


LIBEXEC=$(cd "${WHEREAMI}/.." && pwd)

[ $# -gt 0 ] || die "Usage: ${WHOAMI} command [args]"

#
# Handle special-case commands
#

COMMAND="$1"
shift

case "${COMMAND}" in

    # This is done here to cut back on the number of execs.
    invoke)
	# Invoke a method on an instance of a class
	[ $# -ge 3 ] \
	    || die "Usage: ${WHOAMI} type instance method [ args ]"

	TYPE=$1
	WHICH=$2
	OP=$3
	shift 3

	RUN="${WHEREAMI}/../classes/${TYPE}"
	[ -d "${RUN}" ] || die "INTERNAL ERROR: Unknown class ${TYPE}"

	RUN="${RUN}/${WHICH}"
	[ -d "${RUN}" ] || die "Unknown ${TYPE} '${WHICH}'"

	RUN="${RUN}/${OP}"
	[ -x "${RUN}" ] \
	    || die "INTERNAL ERROR: ${TYPE} ${WHICH} has no operator '${OP}'"

	exec "${RUN}" "$@"
	;;

    *)
	INTERNAL_COMMAND="__INTERNALS__/${COMMAND}"
	[ -x "${INTERNAL_COMMAND}" ] && exec "${INTERNAL_COMMAND}" "$@"	   
	die "Usage: ${WHOAMI} command [args]"
	;;

esac

die "Should not be reached."
