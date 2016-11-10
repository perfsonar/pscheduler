#
# Thread-Safe versions of popular things
#

import threading

class ThreadSafeDictionary(dict):

    """
    Conventional python dictionary with forced thread safety
    """

    def __init__(self):
        vars(self).update( lock=threading.Lock() )

    def __repr__(self):
        with self.lock:
            return super(ThreadSafeDictionary, self).__repr__()

    # Don't lock __str()__; it causes deadlocks.

    def __lt__(self, other):
        with self.lock:
            return super(ThreadSafeDictionary, self).__lt__(other)

    def __le__(self, other):
        with self.lock:
            return super(ThreadSafeDictionary, self).__le__(other)

    def __eq__(self, other):
        with self.lock:
            return super(ThreadSafeDictionary, self).__eq__(other)

    def __ne__(self, other):
        with self.lock:
            return super(ThreadSafeDictionary, self).__ne__(other)

    def __gt__(self, other):
        with self.lock:
            return super(ThreadSafeDictionary, self).__gt__(other)

    def __ge__(self, other):
        with self.lock:
            return super(ThreadSafeDictionary, self).__ge__(other)

    def __cmp__(self, other):
        with self.lock:
            return super(ThreadSafeDictionary, self).__cmp__(other)

    def __rcmp__(self, other):
        with self.lock:
            return super(ThreadSafeDictionary, self).__rcmp__(other)

    def __hash__(self):
        with self.lock:
            return super(ThreadSafeDictionary, self).__hash__()

    def __nonzero__(self):
        with self.lock:
            return super(ThreadSafeDictionary, self).__nonzero__()

    def __unicode__(self):
        with self.lock:
            return super(ThreadSafeDictionary, self).__unicode__()

    def __getattr__(self, name, value):
        with self.lock:
            return super(ThreadSafeDictionary, self).__getattr__(name, value)

    def __setattr__(self, name, value):
        with self.lock:
            return super(ThreadSafeDictionary, self).__setattr__(name, value)

    def __delattr__(self, name):
        with self.lock:
            return super(ThreadSafeDictionary, self).__delattr__(name)

    def __get__(self, name, value):
        with self.lock:
            return super(ThreadSafeDictionary, self).__get__(name, value)

    def __set__(self, name, value):
        with self.lock:
            return super(ThreadSafeDictionary, self).__set__(name, value)

