#
# Database Cursor
#

import pscheduler
import sys

from .log import log

this = sys.modules[__name__]

this.dsn = None
this.cursor = None

def dbcursor_init(dsn):
    """Connect to the database"""
    if this.cursor is None:
        this.cursor = pscheduler.pg_cursor(dsn)
        this.dsn = dsn


def dbcursor():
    if this.cursor.closed:
        log.warning("Database cursor is closed; reconnecting")
        this.cursor = None
        dbcursor_init(this.dsn)
    return this.cursor


def dbcursor_query(query,
                   args=[],
                   onerow=False   # Require exactly one row returned
                   ):
    """
    Run a query against a cursor, catching anything that arises from
    the rowcount being < 0 and throwing an error.
    """
    cursor = dbcursor()
    cursor.execute(query, args)
    rows = cursor.rowcount
    if rows < 0:
        raise psycopg2.Error("No results returned; may be an internal problem")
    if onerow and rows != 1:
        raise psycopg2.Error("Expected one row; got %d" % cursor)
    return cursor
