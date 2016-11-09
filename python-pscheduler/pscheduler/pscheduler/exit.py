"""
Exit the program gracefully when certain signals arrive.
"""

import signal

def __exit_handler(signum, frame):
    # TODO: Remove this.
    print "Exiting on signal", signum
    exit(0)

def set_graceful_exit():
    """
    Set up a graceful exit when certain signals arrive.
    """
    for sig in [ signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM ]:
        signal.signal(sig, __exit_handler)
