"""
Exit the program gracefully when certain signals arrive.
"""

import threading
import signal
import sys

from threading import Thread,Semaphore
import collections


this = sys.modules[__name__]
this.lock = threading.Lock()
this.exit_worker = None
this.exit_barrier = None
this.exit_list = []
this.finish_barrier = None


def __graceful_exit_worker():
    """
    Wait for the exit lock to become available, then call all of the
    exit calls.
    """
    #print "GEW START"
    assert this.exit_barrier is not None
    # Wait for the handler to tell us we're exting
    this.exit_barrier.wait()
    #print "GEW PAST BARRIER"
    with this.lock:
        #print "GEW DOING EXIT WORK"
        for call in this.exit_list:
            #print "GEW calling", call
            call()
    # Let on_graceful_exit know it can exit
    this.finish_barrier.wait()
    #print "GEW DONE"


def on_graceful_exit(call):
    """
    Add an item to the list of calls to be made during a graceful
    exit.  If the exit worker isn't running, start it.
    """

    #print "OGE", call

    if not isinstance(call, collections.Callable):
        raise ValueError("%s is not callable", call)

    with this.lock:

        if this.exit_worker is None and this.exit_barrier is None:
            #print "OGE INITIALIZING"
            this.finish_barrier = threading.Barrier(2)
            this.exit_barrier = threading.Barrier(2)
            this.exit_worker = threading.Thread(
                name="Exit Worker",
                target=lambda: __graceful_exit_worker())
            this.exit_worker.setDaemon(True)
            this.exit_worker.start()

        #print "OGE APPENDING", call
        this.exit_list.append(call)

    #print "OGE DONE"


def __exit_handler(signum, frame):
    """
    Let the worker go.  This doesn't do much of anything because it's
    called from inside a signal handler.
    """
    #print "EH START"
    with this.lock:
        exit_barrier = this.exit_barrier

    if exit_barrier is not None:
        # Meet up with the worker
        this.exit_barrier.wait()
        #print "EH FIRST BARRIER"
        # Wait for the worker to be done
        this.finish_barrier.wait()
        #print "EH HANDLER FINISHED"
    #print "EH DONE"
    sys.exit(0)


def set_graceful_exit():
    """
    Set up a graceful exit when certain signals arrive.
    """

    for sig in [signal.SIGHUP,
                signal.SIGINT,
                signal.SIGQUIT,
                signal.SIGTERM]:
        signal.signal(sig, __exit_handler)
