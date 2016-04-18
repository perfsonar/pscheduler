"""
Functions for connecting to the pScheduler database
"""

import psycopg2

def pg_connection(dsn='', autocommit=True):
    """
    Connect to the database, and return a handle to it

    Arguments:

    dsn - A data source name to use in connecting to the database.  If
    the string begins with an '@', the remainder will be treated as
    the path to a file where the value can be retrieved.

    autocommit - Whether or not commits are done automatically when
    quesies are issued.
    """

    # Read the DSN from a file if requested
    if dsn.startswith('@'):
        with open(dsn[1:], 'r') as dsnfile:
            dsn = dsnfile.read().replace('\n', '')

    pg = psycopg2.connect(dsn)
    if autocommit:
        pg.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    return pg


def pg_cursor(dsn='', autocommit=True):
    """
    Connect to the database, and return a cursor.

    Arguments:

    dsn - A data source name to use in connecting to the database.  If
    the string begins with an '@', the remainder will be treated as
    the path to a file where the value can be retrieved.

    autocommit - Whether or not commits are done automatically when
    quesies are issued.
    """

    pg = pg_connection(dsn, autocommit)
    return pg.cursor()


# TODO: Need a routine that does the select wait currently
# rubberstamped into the services to do timed waits for notifications.
