#!/usr/bin/python3
"""
test for the Log module.
"""

import os
import signal
import time
import unittest

from base_test import PschedTestBase

from pscheduler.log import Log


class TestLog(PschedTestBase):
    """
    Log tests.
    """

    def test_log(self):
        """Logging tests"""

        # Not much to test here but exercise the code nonetheless
        # for regression/coverage.

        log = Log(verbose=False, prefix='test')

        log.debug("Invisible debug.")

        try:
            raise ValueError("Test exception")
        except ValueError:
            log.exception("Test exception with message")

        for num in range(1, 5):
            log.debug("Debug")
            log.info("Info")
            log.warning("Warning")
            log.error("Error")
            log.critical("Crtitical")
            os.kill(os.getpid(),
                    signal.SIGUSR1 if (num % 2) != 0 else signal.SIGUSR2)


    # TODO: This needs a test of the pickler used to pass data to
    # child processes.


if __name__ == '__main__':
    unittest.main()
