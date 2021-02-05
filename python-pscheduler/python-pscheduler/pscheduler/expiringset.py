"""
Set where items expire after a period of time
"""

import datetime

from .log import Log

class ExpiringSet(object):

    """This class implements a keyed set of objects that are constructed
    by a lambda and retrievable until an expiration time.  After that,
    they are destroyed (also by a lambda) and the next request for the
    same key will create a new one.
    """

    def __init__(self,
                 creator=None,
                 destroyer=None,
                 purge_interval=None,
                 log=None):
        """Create an ExpiringSet.  Parameters:

        creator - lambda key, data: ... - Creates an object based on
        the data, which can be any Python type.

        destroyer - lambda obj: ... - Does any necessary teardown of
        the object when it is removed from the set (e.g., closing of
        connections).

        purge_interval - A Python datetime.timedelta that indicates
        how often the set should be purged of expired objects.  If
        None, objects will never be purged from the set unless purge()
        is called.

        log - Optional pScheduler logger
        """
        self.items = {}

        default_creator = lambda k, d: k
        self.creator = creator if creator is not None else default_creator
        if not isinstance(self.creator, type(default_creator)):
            raise ValueError("Creator must be a function")

        default_destroyer = lambda obj: obj
        self.destroyer = destroyer if destroyer is not None else default_destroyer
        if not isinstance(self.destroyer, type(default_destroyer)):
            raise ValueError("Destroyer must be a function")

        if purge_interval is not None and not isinstance(purge_interval, datetime.timedelta):
            raise ValueError("Purge interval must be a timedelta")
        self.purge_interval = purge_interval
        self.next_purge = datetime.datetime.now() + purge_interval if purge_interval is not None else None

        if log is not None and not isinstance(log, Log):
            raise ValueError("Log be a pScheduler logger")
        self.log = log


    def _debug(self, message):
        if self.log is not None:
            self.log.debug(message)



    def expire(self, key, missing_ok=False):
        """Force immediate expiration and purging of an object"""

        self._debug("Forced expiration of %s" % (key))
        if key in self.items or not missing_ok:
            self.destroyer(self.items[key]["item"])
            del self.items[key]


    def purge(self, force=True):
        """Purge expired objects if it's time to do so immediately if requested."""

        if ( self.next_purge is None or datetime.datetime.now() < self.next_purge ) \
           and not force:
            return

        self._debug("Purging")

        now = datetime.datetime.now()

        for key in self.items:
            item = self.items[key]
            if item["expires"] < now:
                self.expire(key)

        self._debug("Done purging")

        self.next_purge = now + self.purge_interval



    def __call__(self, key, data, cache_time=None):
        """Fetch an item from the cache, creating a new one if necessary.

        key - A key used to identify the item

        data - Arbitrary data used in creating the item, passed to the
        creation lambda.

        cache_time - How long the item should live in the cache after
        creation.  None will create a new item on each call.  Fetching
        with a different cache time will change an existing item's
        cache time effictive after this fetch.
        """

        assert cache_time is None or isinstance(cache_time, datetime.timedelta), \
            "Cache time must be a timedelta"

        self.purge(force=False)

        item_record = self.items.get(key, None)

        # If there was a record but it's expired, get rid of it so we can make a new one.
        if item_record is not None and item_record["expires"] < datetime.datetime.now():
                self._debug("Item '%s' has expired," % (key))
                self.expire(key)
                item_record = None

        # No record means we need one, no matter how we got there.
        if item_record is None:
            item = self.creator(key, data)
            item_record = { "item": item }
            self.items[key] = item_record
            self._debug("Created item '%s'" % (key))

        else:

            item = item_record["item"]
            self._debug("Fetched existing item '%s'" % (key))


        if self.purge_interval is not None:
            self.items[key]["expires"] = datetime.datetime.now() \
                                             + ( cache_time if cache_time is not None
                                                 else datetime.timedelta(seconds=0) )
        self.items[key]["cache_time"] = cache_time
        self._debug("Caching for %s" % (str(cache_time)))

        return item
