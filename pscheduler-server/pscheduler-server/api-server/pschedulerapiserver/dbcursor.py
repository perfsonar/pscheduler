#
# Database Cursor
#

import pscheduler
import psycopg2
import sys
import threading
import time

from .log import log

module = sys.modules[__name__]

module.tries = 10
module.interval = 0.5

module.threadlocal = threading.local()

module.dsn = None   # DSN for DB connection


def dbcursor_init(dsn):
    """Initialize the module.  Yes, this is global state."""
    module.dsn = dsn



class DBCursor:

    def __init__(self):
        self.db = None
        self.ccursor = None  # Dodges conflict with a method name.


    def cursor(self):
        """Get the cursor, reconnecting if necessary."""

        # Make sure we have a working database connection

        if self.db is None or self.db.closed:

            # Reset everything.

            self.db = None
            self.ccursor = None

            assert (module.dsn is not None)

            tries = module.tries

            while tries:
                try:
                    self.db = pscheduler.pg_connection(module.dsn, name="api")
                    break
                except psycopg2.OperationalError as ex:
                    reason = ex
                    tries -= 1
                    log.debug("Attempt failed, %d left", tries)
                    time.sleep(module.interval)

            if self.db is None:
                log.warning("Failed to connect to the database.")
                raise reason;

        # Make sure we have a cursor.

        if self.ccursor is None or self.ccursor.closed():
            self.ccursor = self.db.cursor()

        return self.ccursor



def dbcursor():
    """Get this thread's database cursor"""
    return getattr(threadlocal, "cursor", DBCursor()).cursor()


def dbcursor_query(query,
                   args=[],
                   onerow=False,  # Require exactly one row returned
                   tries=2        # Times to try in the face of errors
                   ):
    """
    Run a query against a cursor, catching anything that arises from
    the rowcount being < 0 and throwing an error.
    """

    log.debug("QUERY: %s, %s", query, args)

    while tries > 0:

        cursor = dbcursor()

        try:
            cursor.execute(query, args)
        except psycopg2.OperationalError as ex:
            log.debug("Operational Error: %s", ex)
            cursor.close()
            tries -= 1
            if tries == 0:
                raise psycopg2.Error("Too many tries to run the query; giving up")
            continue
        except Exception as ex:
            if ex.args:
                text = str(ex)
                location = text.find("\nCONTEXT: ")
                if location > -1:
                    ex.args = (text[0:location],)
            log.debug("EX: %s %s", type(ex), ex)
            raise ex

        break

    rows = cursor.rowcount

    if rows < 0:
        raise psycopg2.Error("No results returned; may be an internal problem")
    if onerow and rows != 1:
        raise psycopg2.Error("Expected one row; got %d" % cursor)

    log.debug("QUERY returned %s rows", rows)

    return cursor
