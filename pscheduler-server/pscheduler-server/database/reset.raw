#!/bin/sh
#
# Do a full reset on the database
#

if [ $(id -u) -ne 0 ]
then
    echo "This must be done as root." 1>&2
    exit 1
fi

if [ -t 0 -a -t 1 -a -t 2 ]
then
    cat <<EOF

WARNING

You are about to obliterate the contents of the pScheduler database on
this host.  Please confirm this by typing today's date in YYYY-MM-DD
format at the prompt below.

EOF
    printf "Confirm (YYYY-MM-DD): "
    read DATE
    if [ "${DATE}" != "$(date +%F)" ]
    then
	printf "\nDate does not match today's date.  Doing nothing.\n\n"
	exit 1
    fi

    printf "\nResetting database..."
fi


# TODO: When we make databases remotable, this will need to pull
# information from the DSN file.


# Tear down the existing database
postgresql-load '__DATADIR__/database-teardown.sql'


# Build up a new one
postgresql-load '__DATADIR__/database-build-super.sql'
postgresql-load --role '__ROLE__' '__DATADIR__/database-build.sql'


# Restore the password
if ! [ -f '__PASSWORDFILE__' -a -r '__PASSWORDFILE__' ]
then
    echo "Can't read password from __PASSWORDFILE__"
    exit 1
fi

(
    printf "ALTER ROLE __ROLE__ WITH UNENCRYPTED PASSWORD '"
    tr -d "\n" < '__PASSWORDFILE__'
    printf "';\n"
) | postgresql-load


# If the ticker is running, it will restart and do this, but in case
# it isn't, make sure everything is in order.
#
# TODO: This will have to be a separate program once the database
# remotable.

postgresql-load --role '__ROLE__' <<EOF
\c pscheduler
DO \$$
BEGIN
    PERFORM cold_boot();
END;
\$$
EOF



[ -t 0 -a -t 1 -a -t 2 ] \
    && printf " Done.  Hope you meant to do that.\n\n"


exit 0
