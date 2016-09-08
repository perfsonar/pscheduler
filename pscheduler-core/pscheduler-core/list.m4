#!/bin/sh
#
# List instances of a pScheduler class
#

# TODO: This is probably not used anywhere but was brought along just
# in case.

WHOAMI=$(basename $0)

if [ $# -ne 1 ]
then
    echo "Usage: list type" 1>&2
    exit 1
fi

TYPE=$1
shift

case "${TYPE}" in
    test|tool|archiver)
	true
	;;
    *)
	echo "Unknown type ${TYPE}" 1>&2
	exit 1
	;;
esac

DIR="__CLASSES__/${TYPE}"
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
