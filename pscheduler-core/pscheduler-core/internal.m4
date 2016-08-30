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

    list)
	# List the instances of a given class
	[ $# -eq 1 ] || die "Usage: list type"
	TYPE=$1
	shift
	case "${TYPE}" in
	    test|tool|archiver)
		true
		;;
	    *)
		die "Unknown type ${TYPE}"
		;;
	esac
	DIR="${LIBEXEC}/classes/${TYPE}"
	if [ ! -d "${DIR}" ]
	then
	    echo '[]'
	    # No directory means nothing of the type installed.
	    exit 0
        fi
	printf '['
	# This is a POSIX-clean equivalent to find . -type d -maxdepth 1
	( cd "${DIR}" && find . -type d ) \
	    | sed -e 's|^./||' \
	    | egrep -ve '^\.' \
	    | grep -v / \
	    | tr '\n' '/' \
	    | sed -e 's|/$||; s|/|", "|g; s|^|"|; s|$|"|'
	printf ']\n'
	exit $?
	;;


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

    nothing)
	echo "Doing nothing (stdout)"
	echo "Doing nothing (stderr)" 1>&2
	exit 0
	;;

    *)
	die "Usage: ${WHOAMI} command [args]"
	;;

esac

die "Should not be reached."
