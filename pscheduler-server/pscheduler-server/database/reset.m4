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

# TODO: This should probably be a stored procedure in the database
# that calls a xxx_reset() for every table that has one.

postgresql-load --role __ROLE__ <<EOF
\c __DATABASE__
DO \$\$
BEGIN
    DELETE FROM task;
    DELETE FROM http_queue;
    PERFORM warm_boot();
END;
\$\$ LANGUAGE plpgsql;
EOF


[ -t 0 -a -t 1 -a -t 2 ] \
    && printf " Done.  Hope you meant to do that.\n\n"
