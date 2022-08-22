#
# Thread-Safe versions of popular things and other thread-related
# classes.
#

import queue
import threading


class ThreadSafeSet:

    """
    A set that uses queues to assure thread safety.

    Note that this object is intended to be read at least as
    frequently as it is written.  Failure to do so will result in adds
    and removes stacking up in the internal queue.
    """

    __MSG_ADD = 0
    __MSG_REMOVE = 1

    def __init__(self):
        self.__dict = {}
        self.__lock = threading.Lock()
        self.__queue = queue.Queue()


    def __clear_queue(self):
        """Do everything in the queue"""
        while not self.__queue.empty():
            try:
                (message, item) = self.__queue.get_nowait()
            except queue.Empty:
                break

            if message == self.__MSG_ADD:
                self.__dict[item] = 1
            elif message == self.__MSG_REMOVE:
                del self.__dict[item]


    def __len__(self):
        with self.__lock:
            self.__clear_queue()
            return len(self.__dict)


    def __contains__(self, item):
        with self.__lock:
            self.__clear_queue()
            return item in self.__dict


    def add(self, item):
            self.__queue.put((self.__MSG_ADD, item))


    def remove(self, item):
        with self.__lock:
            self.__clear_queue()
            if item not in self.__dict:
                raise KeyError(item)
            self.__queue.put((self.__MSG_REMOVE, item))


    def items(self):
        with self.__lock:
            self.__clear_queue()
            return list(self.__dict.keys())




# Source: https://stackoverflow.com/a/6894023
# LICENSE: CC-BY-SA 4.0

class ThreadWithReturnValue(threading.Thread):
    """
    Thread with a join() that returns whatever the target did.
    """

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return
