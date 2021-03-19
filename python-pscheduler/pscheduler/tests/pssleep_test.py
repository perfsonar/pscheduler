#!/usr/bin/env python3
"""
test for the sleep module.
"""

import datetime
import unittest

from base_test import PschedTestBase

from pscheduler.pstime import time_now
from pscheduler.pssleep import sleep_until



class TestSleep(PschedTestBase):
    """
    Sleep Tests
    """

    def test_sleep_until(self):
        """Sleep until time"""

        # Invalid values
        self.assertRaises(ValueError, sleep_until, 12345)
        self.assertRaises(ValueError, sleep_until, "Not a time.")

        # Time in the past
        start = time_now()
        sleep_until("2000-01-01T00:00:00-00:00")
        elapsed = time_now() - start
        self.assertEqual(elapsed < datetime.timedelta(seconds=0.1), True)

        # Time in the near future
        start = time_now()
        target = start + datetime.timedelta(seconds=0.1)
        sleep_until(target)
        elapsed = time_now() - start
        self.assertGreaterEqual(elapsed, datetime.timedelta(seconds=0.1))
        self.assertLess(elapsed,datetime.timedelta(seconds=1.0))


if __name__ == '__main__':
    unittest.main()
