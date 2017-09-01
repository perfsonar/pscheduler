"""
Exit the program gracefully when certain signals arrive.
"""

import threading
import signal
import sys

__LOCK = threading.Lock()
__EXIT_WORKER = None
__EXIT_LOCK = None
__EXIT_LIST = []


def __graceful_exit_worker():
    """
    Wait for the exit lock to become available, then call all of the
    exit calls.
    """
    global __EXIT_LOCK
    global __EXIT_LIST

    #print "GEW START"
    assert __EXIT_LOCK is not None
    __EXIT_LOCK.acquire()
    #print "GEW ACQUIRED"
    for call in __EXIT_LIST:
        #print "GEW calling", call
        call()
    #print "GEW DONE"


def on_graceful_exit(call):
    """
    Add an item to the list of calls to be made during a graceful
    exit.  If the exit worker isn't running, start it.
    """

    #print "OGE", call

    if not callable(call):
        raise ValueError("%s is not callable", call)

    global __LOCK
    global __EXIT_WORKER
    global __EXIT_LOCK

    with __LOCK:

        if __EXIT_WORKER is None and __EXIT_LOCK is None:
            __EXIT_LOCK = threading.Lock()
            __EXIT_LOCK.acquire()
            __EXIT_WORKER = threading.Thread(
                target=lambda: __graceful_exit_worker())
            __EXIT_WORKER.setDaemon(True)
            __EXIT_WORKER.start()

        __EXIT_LIST.append(call)


def __exit_handler(signum, frame):
    """
    Let the worker go.  This doesn't do much of anything because it's
    called from inside a signal handler.
    """
    global __LOCK
    global __EXIT_LOCK

    #print "EH START"
    with __LOCK:
        if __EXIT_LOCK is not None:
            __EXIT_LOCK.release()
            #print "EH RELEASE"
    #print "EH DONE"
    sys.exit(0)


def set_graceful_exit():
    """
    Set up a graceful exit when certain signals arrive.
    """

    global __LOCK
    global __EXIT_WORKER
    global __EXIT_LOCK

    for sig in [signal.SIGHUP,
                signal.SIGINT,
                signal.SIGQUIT,
                signal.SIGTERM]:
        signal.signal(sig, __exit_handler)
