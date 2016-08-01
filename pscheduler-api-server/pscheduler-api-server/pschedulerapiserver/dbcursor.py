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
