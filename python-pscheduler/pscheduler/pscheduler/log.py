"""
Functions for Logging
"""

import codecs
import logging
import logging.handlers
import os
import pickle
import signal
import sys
import time
import traceback


# Logging Constants

# Priorities
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


# POSIX log Facilities
#
# These use getattr because this list is generated from syslog.h and may differ
# between systems.

auth = getattr(logging.handlers.SysLogHandler, "LOG_AUTH", None)
cron = getattr(logging.handlers.SysLogHandler, "LOG_CRON", None)
daemon = getattr(logging.handlers.SysLogHandler, "LOG_DAEMON", None)
kern = getattr(logging.handlers.SysLogHandler, "LOG_KERN", None)
lpr = getattr(logging.handlers.SysLogHandler, "LOG_LPR", None)
mail = getattr(logging.handlers.SysLogHandler, "LOG_MAIL", None)
news = getattr(logging.handlers.SysLogHandler, "LOG_NEWS", None)
user = getattr(logging.handlers.SysLogHandler, "LOG_USER", None)
uucp = getattr(logging.handlers.SysLogHandler, "LOG_UUCP", None)
local0 = getattr(logging.handlers.SysLogHandler, "LOG_LOCAL0", None)
local1 = getattr(logging.handlers.SysLogHandler, "LOG_LOCAL1", None)
local2 = getattr(logging.handlers.SysLogHandler, "LOG_LOCAL2", None)
local3 = getattr(logging.handlers.SysLogHandler, "LOG_LOCAL3", None)
local4 = getattr(logging.handlers.SysLogHandler, "LOG_LOCAL4", None)
local5 = getattr(logging.handlers.SysLogHandler, "LOG_LOCAL5", None)
local6 = getattr(logging.handlers.SysLogHandler, "LOG_LOCAL6", None)
local7 = getattr(logging.handlers.SysLogHandler, "LOG_LOCAL7", None)


# Internal-use name of environment variable
STATE_VARIABLE = 'PSCHEDULER_LOG_STATE'


class Log(object):

    """
    Logger class.

    Sendig SIGUSR1 will force the log level to DEBUG.  Sending SIGUSR2
    will set it to whatever level was previously set.

    If the 'propagate' parameter is True, the logging state (level,
    forced debug, quiet) will be passed along to any child process
    which instantiates a Log instance.  This happens via the
    environment, so anything that scrubs it clean (e.g., sudo) will
    cause this feaure not to function.  Also note that if there is
    more than one propagating logger present in a process, the
    last-set group of parameters will be put into the environment.
    """

    def __syslog_handler_deinit(self):
        """
        Kill off the syslog handler; called when a log event fails.
        """

        try:
            if self.syslog_handler is not None:
                self.logger.removeHandler(self.syslog_handler)
                self.syslog_handler = None
        except AttributeError:
            # Don't care if it's not there.
            pass

    def __syslog_handler_init(self):
        """
        Initialize the syslog handler if it hasn't been
        """

        if not hasattr(self, "syslog_handler"):
            self.syslog_handler = None

        if self.syslog_handler is None:
            try:
                # PORT: /dev/log is Linux-specific.
                self.syslog_handler = logging.handlers.SysLogHandler(
                    '/dev/log', facility=self.facility)
                self.syslog_handler.setFormatter(
                    logging.Formatter(
                        fmt='%(name)s %(levelname)-8s %(message)s'
                    )
                )
                self.logger.addHandler(self.syslog_handler)
            except:
                self.__syslog_handler_deinit()

    def __init__(self,
                 name=None,     # Name for log entries
                 prefix=None,   # Prefix for name (e.g., prefix/progname)
                 level=INFO,    # Logging level
                 facility=local4,  # Log facility
                 debug=False,   # Force level to DEBUG
                 verbose=False,  # Log to stderr, too.
                 quiet=None,   # Don't log anything on startup  (See below)
                 signals=True,  # Enable debug on/off with SIGUSR1/SIGUSR2
                 propagate=False  # Pass debug state on to child processes
                 ):

        #
        # Handle the parameters
        #

        if name is None:
            name = os.path.basename(sys.argv[0])
        assert isinstance(name, str)

        if prefix is not None:
            assert isinstance(prefix, str)
            name = prefix + "/" + name

        self.facility = facility

        if debug:
            level = DEBUG

        self.is_propagating = propagate

        # This prevents verbose() from choking on this being undefined.
        self.is_verbose = False

        if quiet is None:
            quiet = False
            forced_quiet = False
        else:
            forced_quiet = quiet

        self.is_quiet = quiet

        self.forced_debug = debug

        #
        # Inherit state from the environment
        #

        state_exception = None
        if STATE_VARIABLE in os.environ:

            try:
                depickled = pickle.loads(
                    codecs.decode(
                        bytes(os.environ[STATE_VARIABLE], "ascii")
                        , "base64"))

                facility = depickled['facility']
                assert isinstance(facility, int)

                level = depickled['last_level']
                assert isinstance(level, int)

                self.forced_debug = depickled['forced_debug']
                assert isinstance(self.forced_debug, bool)

                self.is_quiet = depickled['is_quiet']
                assert isinstance(self.is_quiet, bool)

            except Exception as ex:
                state_exception = ex

        #
        # Set up the logger
        #

        self.logger = logging.getLogger(name)
        self.logger.propagate = False

        self.syslog_handler = None
        self.__syslog_handler_init()

        # Stderr
        self.stderr_handler = logging.StreamHandler(sys.stderr)
        self.stderr_handler.setFormatter(
            logging.Formatter(
                fmt='%(asctime)s %(message)s',
                datefmt='%Y-%m-%dT%H:%M:%S'
            )
        )
        # Don't add this handler; verbose will cover it.

        #
        # Get everything set to go
        #

        self.verbose(verbose)
        self.level(level, save=True)
        self.set_debug(self.forced_debug)
        self.__update_env()

        # Grab signals and make them non-interrupting
        # PORT: How portable is this?
        if signals:
            signal.signal(signal.SIGUSR1, self.sigusr1)
            signal.signal(signal.SIGUSR2, self.sigusr2)
            signal.siginterrupt(signal.SIGUSR1, False)
            signal.siginterrupt(signal.SIGUSR2, False)

        if (not self.is_quiet) and (not forced_quiet):
            self.info("Started")


        # If there was an exception while depickling the current
        # state, log that.

        if state_exception:
            self.warning("Failed to decode %s '%s': %s"
                         % (STATE_VARIABLE, os.environ[STATE_VARIABLE], state_exception))



    def __update_env(self):
        """
        (INTERNAL USE ONLY) Update the environment variable passed to
        child processes to pre-set the state.
        """
        if self.is_propagating:
            to_pickle = {
                'forced_debug': self.forced_debug,
                'facility': self.facility,
                'last_level': self.last_level,
                'is_quiet': self.is_quiet
            }
            os.environ[STATE_VARIABLE] = codecs.encode(
                pickle.dumps(to_pickle), "base64").decode()

    def verbose(self, state):
        "Toggle verbosity (logging to stderr)"
        if state == self.is_verbose:
            return

        if state:
            self.logger.addHandler(self.stderr_handler)
        else:
            self.logger.removeHandler(self.stderr_handler)

        self.is_verbose = state

    def level(self, level, save=True):
        "Set the log level"
        assert level in [DEBUG, INFO, WARNING, ERROR, CRITICAL]
        self.logger.setLevel(level)
        if save:
            self.last_level = level
        self.__update_env()

    # Logging

    def log(self, level, format, *args):
        self.__syslog_handler_init()
        try:
            message = format % args
            lines = message.split("\n")
            while lines[0] == "":
                del lines[0]
            while lines[-1] == "":
                del lines[-1]
            for line in lines:
                self.logger.log(level, line)
        except Exception:
            self.__syslog_handler_deinit()

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

    def exception(self, message=None):
        "Log an exception as an error and debug if we're doing that."
        extype, ex, tb = sys.exc_info()
        message = "Exception: %s%s%s" % (
            message + ': ' if message is not None else '',
            ''.join(traceback.format_exception_only(extype, ex)),
            ''.join(traceback.format_exception(extype, ex, tb)).strip()
        )
        if self.forced_debug:
            self.debug(message)
        else:
            self.error(message)

    # Forced setting of debug level

    def sigusr1(self, signum, frame):
        self.set_debug(True)

    def sigusr2(self, signum, frame):
        self.set_debug(False)

    def set_debug(self, state):
        "Turn debugging on or off, remembering the last-set level"

        if state:
            self.level(DEBUG, save=False)
            self.debug("Debug started")
        else:
            self.debug("Debug discontinued")
            self.level(self.last_level)

        self.forced_debug = state
        self.__update_env()


    def is_forced_debugging(self):
        """Return whether or not forced debug is on"""
        return self.forced_debug


# Test program

if __name__ == "__main__":

    log = Log(verbose=True, prefix='test')

    log.debug("Invisible debug.")

    try:
        raise ValueError("Test exception")
    except Exception:
        log.exception("Test exception with message")

    for num in range(1, 5):
        log.debug("Debug")
        log.info("Info")
        log.warning("Warning")
        log.error("Error")
        log.critical("Crtitical")
        os.kill(os.getpid(),
                signal.SIGUSR1 if (num % 2) != 0 else signal.SIGUSR2)
        time.sleep(1)

    log.info("\n\nThis\n\nis\na\nmulti-line\nentry.\n\n\n")
