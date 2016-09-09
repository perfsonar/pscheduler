#!/bin/sh
#
# Warm boot the database
#

postgresql-load --role __ROLE__ <<EOF
\c __DATABASE__
DO \$\$
BEGIN
    PERFORM warm_boot();
END;
\$\$ LANGUAGE plpgsql;
EOF
