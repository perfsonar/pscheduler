"""
Functions for connecting to the pScheduler database
"""

import datetime
import errno
import inspect
import os
import psycopg2
import select
import sys
import threading

from dateutil.tz import tzlocal

from .filestring import string_from_file
from .psselect import polled_select


def pg_connection(dsn='', autocommit=True, name=None):
    """
    Connect to the database, and return a handle to it

    Arguments:

    dsn - A data source name to use in connecting to the database.  If
    the string begins with an '@', the remainder will be treated as
    the path to a file where the value can be retrieved.

    autocommit - Whether or not commits are done automatically when
    quesies are issued.
    """

    dsn = string_from_file(dsn)

    if name is None:
        name = os.path.basename(sys.argv[0])

    dsn += " application_name=%s" % (name)

    pg = psycopg2.connect(dsn)
    if autocommit:
        pg.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    return pg




# TODO: Need a routine that does the select wait currently
# rubberstamped into the services to do timed waits for notifications.


#
# Full-featured database connection
#
# TODO: Convert existing code to use this and incorporate functions above.
#

class PgQueryResult(object):

    def __init__(self, cursor):
        self.cursor = cursor
        self.rows = cursor.rowcount
        if self.rows == 0:
            self.cursor.close()

    def __len__(self):
        return self.rows

    def __iter__(self):
        return self

    def __next__(self):
        if self.rows == 0:
            raise StopIteration
        self.rows -= 1
        result = next(self.cursor)
        if self.rows == 0:
            self.cursor.close()
        return result

    def done(self):
        if self.rows > 0:
            self.cursor.close()
            self.rows = 0


class PgConnection(object):

    def __init__(self, dsn, autocommit=True, name=None):

        self.pg = pg_connection(dsn, autocommit=autocommit, name=name)
        self.pending_notifications = {}
        self.lock = threading.Lock()

    #
    # Notifications
    #

    def listen(self, channel):
        """
        Listen for notifications on chanel 'channel'.
        """
        self.pg.cursor().execute("LISTEN %s" % (channel))

    def unlisten(self, channel="*"):
        """
        Cancel listening for notifications on channel 'channel' or all
        channels if none is specified.
        """
        self.pg.cursor().execute("UNLISTEN %s" % (channel))

    def notifications(self):
        """
        Return a deduplicated list of unclaimed notifications, each as a
        tuple of (channel, payload, count)
        """
        result = []
        with self.lock:
            for notification in self.pending_notifications:
                result.append((notification[0],
                               notification[1],
                               self.pending_notifications[notification]))
            self.pending_notifications = {}
        return result

    def __capture_notifications(self):
        """
        INTERNAL USE ONLY: Add and deduplicate notifications to the list
        of those that have happened.
        """

        with self.lock:
            for notification in self.pg.notifies:

                channel = notification.channel
                payload = notification.payload

                key = (channel, payload)

                if key in self.pending_notifications:
                    self.pending_notifications[key] += 1
                else:
                    self.pending_notifications[key] = 1

            del self.pg.notifies[:]


    def wait(self, timeout=None):
        """
        Wait through 'timeout' (in seconds) for a notification, or forever
        if it is None.  Return True if a notification was received or
        False otherwise.
        """

        if timeout is not None:
            timeout = float(timeout)

        while True:
            try:
                selected = polled_select([self.pg], [], [], timeout)
                break
            except select.error as ex:
                err_no, message = ex
                if err_no == errno.EINTR:
                    # TODO: This needs to adjust the time remaining
                    continue
                raise ex

        if selected == ([], [], []):
            return False

        self.pg.poll()
        self.__capture_notifications()
        return len(self.pending_notifications) > 0

    def query(self, query, args=[]):
        cursor = self.pg.cursor()
        # TODO: Handle exceptions
        cursor.execute(query, args)
        self.__capture_notifications()
        return PgQueryResult(cursor)

    def commit(self):
        # TODO:  Throw an exception if autocommit?
        self.pg.commit()

    def rollback(self):
        # TODO:  Throw an exception if autocommit?
        self.pg.rowback()



#
# Classes for use in connection pools
#


class DBConnection(object):
    """Database connection with self-awareness of expiration time"""

    def __init__(self, connection, timeout, done_callback, name):
        self.connection = connection
        self._done_callback = done_callback
        self.name = str(name)
        self._expires = datetime.datetime.now(tzlocal()) + timeout

    def returnable(self):
        """Determine if the connection is past its expiration date"""
        return datetime.datetime.now(tzlocal()) > self._expires

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        self.connection.commit()
        self._done_callback(self)

    def cursor(self):
        return self.connection.cursor()

    def __repr__(self):
        return '<%s %s Expires %s>' % (self.__class__.__name__, self.name, self._expires)


class DBConnectionPool():
    """Self-skimming pool of DBConnections"""

    # How long to wait for a connection to become available
    DEFAULT_CONNECTION_TIMEOUT = datetime.timedelta(seconds=5)

    # Connection age before purging
    DEFAULT_SKIM_TIME = datetime.timedelta(seconds=60)


    def _pass(_message):
        """Drop a message on the floor."""
        pass


    def __init__(self, dsn, max_pool_size, name, skim_time=DEFAULT_SKIM_TIME, log_callback=_pass):
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            1,              # Minimum connections
            max_pool_size,  # Maximum connections
            dsn='%s application_name=%s-pool' % (dsn, name))
        self.max_pool_size = max_pool_size
        self.name = name
        self._skim_time = skim_time
        self._next_skim = datetime.datetime.now(tzlocal())
        self._log_callback = log_callback
        self._connections_out = {}
        self._lock = threading.Lock()
        self._pool_semaphore = threading.Semaphore(max_pool_size)


    def _return_callback(self, connection):
        with self._lock:
            try:
                self.pool.putconn(self._connections_out[connection])
                del self._connections_out[connection]
            except KeyError:
                self._log_callback('Connection %s not in the checked out list' % connection)
                pass  # Not there?  Don't care.


    def _skim(self, force=False):
        """Get rid of any connections that say they're returnable."""

        # Do a periodic skim if it's time to do that.
        if (datetime.datetime.now(tzlocal()) < self._next_skim) and not force:
            return

        with self._lock:
            for (connection, dbc) in [
                    (connection, db)
                    for (connection, db) in self._connections_out.items()
                    if connection.returnable()
            ]:
                self.pool.putconn(dbc)
                del self._connections_out[connection]
                self._log_callback('%s: Skimmed orphaned connection "%s"'
                                   % (self.name, connection.name))

        self._next_skim = datetime.datetime.now(tzlocal()) + self._skim_time


    def __call__(self, identifier, timeout=DEFAULT_CONNECTION_TIMEOUT):
        """Get a database connection from the pool, waiting up to 'timeout'
           seconds to get one."""

        self._skim()

        caller = inspect.getframeinfo(inspect.stack()[1][0])
        name = '%s:%s/%s' % (os.path.basename(caller.filename), caller.lineno, str(identifier))

        started = datetime.datetime.now(tzlocal())
        give_up_after = started + timeout
        attempts = 0

        while datetime.datetime.now(tzlocal()) < give_up_after:

            pool_con = None
            try:
                pool_con = self.pool.getconn()  # Already thread-safe
                connection = DBConnection(pool_con, self._skim_time, self._return_callback, name)
                with self._lock:
                    self._connections_out[connection] = pool_con
                if attempts:
                    self._log_callback('Waited %s for a connection' % (datetime.datetime.now(tzlocal()) - started))
                return connection
            except psycopg2.pool.PoolError as ex:
                self._log_callback('%s: Pool error: %s' % (str(identifier), str(ex)))
                if len(self._connections_out) == self.max_pool_size:
                    self._log_callback('%s: Encountered empty pool' % (self.name, connection.name))
                    self.skim()
                    if attempts > 0:
                        time.sleep(0.1)
                    attempts += 1
                    continue
            except Exception as ex:
                # Any other failure is automatic return to the pool if there was one.
                if pool_con is not None:
                    self.pool.putconn(pool_con)
                raise ex

        # Reaching here means the pool is still full.
        raise psycopg2.pool.PoolError('Timed out getting database connection')

    def __repr__(self):
        with self._lock:
            return '<%s %d/%d>' % (self.__class__.__name__,
                                   len(self._connections_out), self.max_pool_size)
