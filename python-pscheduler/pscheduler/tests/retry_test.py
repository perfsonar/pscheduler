"""
test for the Retry module.
"""

import datetime
import unittest

from base_test import PschedTestBase

from pscheduler.retry import RetryPolicy


class TestRetry(PschedTestBase):
    """
    Retry tests.
    """

    def test_retry(self):
        """Retry policy test"""
        policy = RetryPolicy([
            {"attempts": 1, "wait": "PT10S"},
            {"attempts": 4, "wait": "PT1M"},
            {"attempts": 5, "wait": "PT1H"}
        ])

        tens = datetime.timedelta(seconds=10)
        onem = datetime.timedelta(minutes=1)
        oneh = datetime.timedelta(hours=1)

        # sequence of deltas to be returned
        series = [tens, onem, onem, onem, onem, oneh, oneh, oneh, oneh, oneh, None, None]

        for attempt in range(0, 12):
            retry = policy.retry(attempt)
            self.assertEqual(retry, series[attempt])


if __name__ == '__main__':
    unittest.main()
