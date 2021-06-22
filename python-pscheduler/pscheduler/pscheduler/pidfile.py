"""
PID file context manager for use with python-daemon

Source:  http://code.activestate.com/recipes/577911-context-manager-for-a-daemon-pid-file/
License: Dual licensed under the MIT and GPL licenses  (perfSONAR elects MIT.)
"""

import fcntl
import os


class PidFile(object):
    """Context manager that locks a pid file.  Implemented as class
    not generator because daemon.py is calling .__exit__() with no parameters
    instead of the None, None, None specified by PEP-343."""
    # pylint: disable=R0903

    def __init__(self, path):
        self.path = path
        self.pidfile = None

    def __enter__(self):
        if self.path is None:
            return self.pidfile

        self.pidfile = open(self.path, "a+")
        try:
            fcntl.flock(self.pidfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            self.pidfile = None
            raise SystemExit("Already running according to " + self.path)
        self.pidfile.seek(0)
        self.pidfile.truncate()
        self.pidfile.write(str(os.getpid()))
        self.pidfile.flush()
        self.pidfile.seek(0)
        return self.pidfile

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        if self.pidfile is not None:
            try:
                self.pidfile.close()
            except IOError as err:
                # ok if file was just closed elsewhere
                if err.errno != 9:
                    raise
            try:
                os.remove(self.path)
            except IOError:
                pass


# Example usage:
# import daemon
# context = daemon.DaemonContext()
# context.pidfile = PidFile("/var/run/mydaemon")
