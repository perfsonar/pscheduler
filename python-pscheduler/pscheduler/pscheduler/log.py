"""
Functions for Logging
"""

import logging
import logging.handlers
import os
import signal
import sys
import time
import traceback


# Logging Constants

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

class Log():

    """
    Logger class.

    Sendig SIGUSR1 will force the log level to DEBUG.  Sending SIGUSR2
    will set it to whatever level was previously set.
    """

    def __init__(self,
                 name=None,     # Name for log entries
                 prefix=None,   # Prefix for name (e.g., prefix/progname)
                 level=INFO,    # Logging level
                 debug=False,   # Force level to DEBUG
                 verbose=False  # Log to stderr, too.
                 ):

        if name is None:
            name = os.path.basename(sys.argv[0])
        assert type(name) == str

        if prefix is not None:
            assert type(prefix) == str
            name = prefix + "/" + name

        if debug:
            level = DEBUG
      
        self.logger = logging.getLogger(name)

        # Syslog
        self.syslog_handler = logging.handlers.SysLogHandler('/dev/log')
        self.syslog_handler.formatter = logging.Formatter(
            fmt     = '%(name)s %(levelname)-8s %(message)s')
        self.logger.addHandler(self.syslog_handler)

        # Stderr
        self.stderr_handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            fmt     = '%(asctime)s %(message)s',
            datefmt = '%Y-%m-%dT%H:%M:%S')
        self.stderr_handler.setFormatter(formatter)

        self.forced_debug = False
        self.is_verbose = False
        self.verbose(verbose)
        self.level(level)

        # Grab signals and make them non-interrupting
        # TODO: How portable is this?
        signal.signal(signal.SIGUSR1, self.sigusr1)
        signal.signal(signal.SIGUSR2, self.sigusr2)
        signal.siginterrupt(signal.SIGUSR1, False)
        signal.siginterrupt(signal.SIGUSR2, False)

        self.info("Started")



    def verbose(self, state):
        "Toggle verbosity (logging to stderr)"
        if state == self.is_verbose:
            return

        if state:
            self.logger.addHandler(self.stderr_handler)
        else:
            self.logger.removeHandler(self.stderr_handler)


    def level(self, level, save=True):
        "Set the log level"
        assert level in [ DEBUG, INFO, WARNING, ERROR, CRITICAL ]
        self.logger.setLevel(level)
        if save:
            self.last_level = level


    # Logging

    def log(self, level, format, *args):
        self.logger.log(level, format, *args)

    def debug(self, format, *args):
        self.log(DEBUG, format, *args)

    def info(self, format, *args):
        self.log(INFO, format, *args)

    def warning(self, format, *args):
        self.log(WARNING, format, *args)

    def error(self, format, *args):
        self.log(ERROR, format, *args)

    def critical(self, format, *args):
        self.log(CRITICAL, format, *args)

    def exception(self):
        "Log an exception as an error"
        extype, ex, tb = sys.exc_info()
        self.error(
            "Exception: %s%s",
            ''.join(traceback.format_exception_only(extype, ex)),
            ''.join(traceback.format_exception(extype, ex, tb)).strip()
            )


    # Forced setting of debug level

    def sigusr1(self, signum, frame):
        self.set_debug(True)

    def sigusr2(self, signum, frame):
        self.set_debug(False)

    def set_debug(self, state):
        "Turn debugging on or off, remembering the last-set level"

        if state == self.forced_debug:
            self.debug("Debug signal ignored; already %sdebugging",
                       "" if state else "not ")

        if state:
            self.level(DEBUG, save=False)
            self.debug("Debug logging turned on")
        else:
            self.debug("Debug logging turned off")
            self.level(self.last_level)


        self.forced_debug = state



# Test program

if __name__ == "__main__":

    log = Log(verbose=True, prefix='test')

    log.debug("Invisible debug.")

    try:
        raise ValueError("Test exception")
    except Exception as ex:
        log.exception()

    for num in range(1,5):
        log.debug("Debug")
        log.info("Info")
        log.warning("Warning")
        log.error("Error")
        log.critical("Crtitical")
        os.kill( os.getpid(),
                 signal.SIGUSR1 if (num % 2) != 0 else signal.SIGUSR2 )
        time.sleep(1)
