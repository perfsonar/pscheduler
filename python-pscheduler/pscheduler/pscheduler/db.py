"""
Functions for connecting to the pScheduler database
"""

import errno
import os
import psycopg2
import select
import sys

from filestring import string_from_file


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


def pg_cursor(dsn='', autocommit=True, name=None):
    """
    Connect to the database, and return a cursor.

    Arguments:

    dsn - A data source name to use in connecting to the database.  If
    the string begins with an '@', the remainder will be treated as
    the path to a file where the value can be retrieved.

    autocommit - Whether or not commits are done automatically when
    quesies are issued.
    """

    pg = pg_connection(dsn, autocommit, name)
    return pg.cursor()


# TODO: Need a routine that does the select wait currently
# rubberstamped into the services to do timed waits for notifications.


#
# Full-featured database connection
#
# TODO: Convert existing code to use this and incorporate functions above.
#

class PgQueryResult:

    def __init__(self, cursor):
        self.cursor = cursor
        self.rows = cursor.rowcount
        if self.rows == 0:
            self.cursor.close()

    def __len__(self):
        return self.rows

    def __iter__(self):
        return self.cursor

    def next(self):
        if self.rows == 0:
            raise StopIteration
        self.rows -= 1
        result = self.cursor.next()
        if self.rows == 0:
            self.cursor.close()
        return result

    def done(self):
        if self.rows > 0:
            self.cursor.close()
            self.rows = 0


class PgConnection:

    def __init__(self, dsn, autocommit=True, name=None):

        self.pg = pg_connection(dsn, autocommit=autocommit, name=name)
        self.pending_notifications = {}

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
                selected = select.select([self.pg], [], [], timeout)
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
# Test Program
#

if __name__ == "__main__":

    dsn = 'host=127.0.0.1 dbname=pscheduler user=pscheduler password=6ibeARUyecg6YyJpkRnrt1GIugFUoOK3Hb9SEaJD0BJAhxTBgM3XX'

    db = PgConnection(dsn, name="PgConnection-test")

    db.listen("query")
    db.listen("stop")

    run = True
    while run:

        if db.wait(5):

            print "Notified"

            for notification in db.notifications():
                (channel, payload, count) = notification

                if channel == "query":
                    result = db.query("""
                         SELECT table_name
                         FROM information_schema.tables WHERE table_schema = %s
                         LIMIT 5""", ["public"])
                    print len(result), "rows"
                    for row in result:
                        print row[0]
                    print "End of results"
                elif channel == "stop":
                    run = False
                    break

        else:
            print "No notifications"

    db.unlisten()
