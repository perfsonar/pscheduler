#!/usr/bin/python3
"""
Test for rundaterange limit
"""

import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.limit.rundaterange import *


LIMIT = {
    "start": "2019-01-01T00:00:00-04",
    "end":   "2019-12-31T23:59:59-04",
    "overlap": True
}

LIMIT_NO_OVERLAP = {
    "start": "2019-01-01T00:00:00-04",
    "end":   "2019-12-31T23:59:59-04",
    "overlap": False
}


class TestLimitprocessorLimitRunDateRange(PschedTestBase):
    """
    Test the Limit
    """

    def test_data_is_valid(self):
        """Limit Processor / Limit Run Date Range / Data Validation"""

        self.assertEqual(rundaterange_data_is_valid(LIMIT), (True, "OK"))
        self.assertEqual(rundaterange_data_is_valid({ "bad": "value" }),
                         (False, "At /: Additional properties are not allowed ('bad' was unexpected)"))



    def test_limit(self):
        """Limit Processor / Limit Run Date Range / Limit"""

        limit = LimitRunDateRange(LIMIT)

        # In range
        self.assertEqual(
            limit.evaluate({
                "task": {
                    "run_schedule": {
                        "start": "2019-05-04T12:34:56-04",
                        "duration": "PT30S"
                    }
                }
            }),
            { "passed": True }
            )

        # Overlapping
        self.assertEqual(
            limit.evaluate({
                "task": {
                    "run_schedule": {
                        "start": "2018-12-31T23:59:45-04",
                        "duration": "PT30S"
                    }
                }
            }),
            { "passed": True }
            )

        # Out of range
        self.assertEqual(
            limit.evaluate({
                "task": {
                    "run_schedule": {
                        "start": "2012-05-04T12:34:56-04",
                        "duration": "PT30S"
                    }
                }
            }),
            { "passed": False, "reasons": [ "Ranges do not match" ] }
            )



        limit = LimitRunDateRange(LIMIT_NO_OVERLAP)

        # Overlapping
        self.assertEqual(
            limit.evaluate({
                "task": {
                    "run_schedule": {
                        "start": "2018-12-31T23:59:45-04",
                        "duration": "PT30S"
                    }
                }
            }),
            { "passed": False, "reasons": [ "Ranges do not match" ] }
            )




if __name__ == '__main__':
    unittest.main()
