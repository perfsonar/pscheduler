#
# Database Cursor
#

import pscheduler
import sys

# TODO: Don't like the global nature of this.  Do a better job
# encapsulating it.

this = sys.modules[__name__]

this.cursor = None

def dbcursor_init(dsn):
    """Connect to the database"""
    if this.cursor is None:
        this.cursor = pscheduler.pg_cursor(dsn)
        # TODO: What happens if the connection goes south?

def dbcursor():
    return this.cursor
