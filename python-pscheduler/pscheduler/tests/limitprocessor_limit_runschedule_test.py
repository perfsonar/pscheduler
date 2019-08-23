#!/usr/bin/python3
"""
Test for runschedule limit
"""

import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.limit.runschedule import *



LIMIT = {
    "year": [ 2015, 2016, 2017, 2018 ],
    "month": [ { "lower": 1, "upper": 6 } ],
    "week": [],
    "day": [],
    "weekday": [ { "lower": 3, "upper": 6 } ],
    "hour": [3, 4, { "lower": 7, "upper": 11 } ],
    "minute": [ 12,34 ],
    "second": [],
    "overlap": False
}


class TestLimitprocessorLimitRunSchedule(PschedTestBase):
    """
    Test the Limit
    """

    def test_data_is_valid(self):
        """Limit Processor / Limit Run Date Range / Data Validation"""

        self.assertEqual(runschedule_data_is_valid(LIMIT), (True, "OK"))
        self.assertEqual(runschedule_data_is_valid({ "bad": "value" }),
                         (False, "At /: Additional properties are not allowed ('bad' was unexpected)"))



    def test_limit(self):
        """Limit Processor / Limit Run Date Range / Limit"""

        TASK = {
            "task": {
                "run_schedule": {
                    "start": "2019-05-04T12:34:00-04",
                    "duration": "PT30S"
                }
            }
        }


        # Year

        limit = LimitRunSchedule({ "year": [ 2015, 2016, 2017, 2018, 2019 ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": True })

        limit = LimitRunSchedule({ "year": [ 2015, 2016, 2017, 2018 ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": False, "reasons": [ "Mismatch on year" ] })


        # Month

        limit = LimitRunSchedule({ "month": [ { "lower": 1, "upper": 6 } ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": True })

        limit = LimitRunSchedule({ "month": [ { "lower": 7, "upper": 12 } ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": False, "reasons": [ "Mismatch on month" ] })


        # Day

        limit = LimitRunSchedule({ "day": [ { "lower": 1, "upper": 15 } ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": True })

        limit = LimitRunSchedule({ "day": [ { "lower": 16, "upper": 31 } ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": False, "reasons": [ "Mismatch on day" ] })


        # Weekday

        limit = LimitRunSchedule({ "weekday": [ { "lower": 3, "upper": 6 } ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": True })

        limit = LimitRunSchedule({ "weekday": [ { "lower": 0, "upper": 2 } ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": False, "reasons": [ "Mismatch on weekday" ] })


        # Hour

        limit = LimitRunSchedule({ "hour": [ { "lower": 9, "upper": 13 } ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": True })

        limit = LimitRunSchedule({ "hour": [ { "lower": 1, "upper": 6 } ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": False, "reasons": [ "Mismatch on hour" ] })


        # Minute

        limit = LimitRunSchedule({ "minute": [ { "lower": 30, "upper": 40 } ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": True })

        limit = LimitRunSchedule({ "minute": [ { "lower": 45, "upper": 59 } ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": False, "reasons": [ "Mismatch on minute" ] })


        # Second

        limit = LimitRunSchedule({ "second": [ { "lower": 0, "upper": 30 } ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": True })

        limit = LimitRunSchedule({ "second": [ { "lower": 31, "upper": 59 } ] })
        self.assertEqual(limit.evaluate(TASK),
                         { "passed": False, "reasons": [ "Mismatch on second" ] })

        # TODO: Check overlap.



if __name__ == '__main__':
    unittest.main()
