#
# Database Cursor
#

import pscheduler
import psycopg2
import sys
import threading

from .log import log

this = sys.modules[__name__]

this.lock = threading.RLock()
this.threadlocal = threading.local()

this.dsn = None   # DSN for DB connection
this.db = None    # DB connection
this.db_gen = 0   # Generation of DB connection



def dbcursor_init(dsn, reconnect=False, tries=10, interval=0.5):
    """Connect to the database"""

    with this.lock:

        if reconnect:
            log.debug("Reconnecting to database")
            this.db = None

        if this.db is None:
            log.debug("Connecting to database")

            db = None
            reason = None

            while tries:
                try:
                    db = pscheduler.pg_connection(dsn)
                    break
                except psycopg2.OperationalError as ex:
                    reason = ex
                    tries -= 1
                    time.sleep(interval)

            if db is None:
                log.warning("Failed to connect to the database.")
                raise reason;

            log.debug("Successfully connected")

            this.dsn = dsn
            this.db = db
            this.db_gen += 1


def __make_cursor():
    """Make a cursor for this thread."""
    with lock:
        assert (this.db is not None)
        if this.db.closed:
            dbcursor_init(this.dsn, reconnect=True)
        cursor = this.db.cursor()
            
        this.threadlocal.cursor = cursor
        this.threadlocal.db_gen = this.db_gen
    return cursor
    


def dbcursor():

    cursor = getattr(threadlocal, "cursor", __make_cursor())

    if cursor.closed:
        log.warning("Database cursor is closed; reconnecting")
        with lock:
            # Connection died on current connection, time for a new one.
            if this.threadlocal.db_gen == this.db_gen:
                dbcursor_init(this.dsn, reconnect=True)
        cursor = __make_cursor()

    return cursor


def dbcursor_query(query,
                   args=[],
                   onerow=False,  # Require exactly one row returned
                   tries=2        # Times to try in the face of errors
                   ):
    """
    Run a query against a cursor, catching anything that arises from
    the rowcount being < 0 and throwing an error.
    """

    log.debug("Query %s %s" % (query, args))

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
            log.debug("EX: %s", ex)
            log.exception()
            raise ex;

        break

    rows = cursor.rowcount
    log.debug("Returned %d rows", rows)
    if rows < 0:
        raise psycopg2.Error("No results returned; may be an internal problem")
    if onerow and rows != 1:
        raise psycopg2.Error("Expected one row; got %d" % cursor)
    return cursor
