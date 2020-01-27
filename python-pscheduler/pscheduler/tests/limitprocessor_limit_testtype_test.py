#!/usr/bin/python3
"""
Test for testtypelimit
"""

import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.limit.testtype import *


LIMIT = {
    "types": [
        "rtt",
        "trace",
        "latency"
    ]
}

class TestLimitprocessorLimitTestType(PschedTestBase):
    """
    Test the Limit
    """

    def test_data_is_valid(self):
        """Limit Processor / Limit PassFail / Data Validation"""

        self.assertEqual(data_is_valid(LIMIT), (True, "OK"))
        self.assertEqual(data_is_valid({}), (False, "At /: 'types' is a required property"))



    def test_limit(self):
        """Limit Processor / Limit PassFail / Limit"""

        # In the list
        limit = LimitTestType(LIMIT)
        self.assertEqual(limit.evaluate({ "task": { "test": { "type": "rtt" } } }),
                         {"passed": True}
        )

        # Not in the list
        limit = LimitTestType(LIMIT)
        self.assertEqual(limit.evaluate({ "task": { "test": { "type": "not-in-the-list" } } }),
                         { "passed": False, "reasons": [ "Test type not in list"] }
        )





if __name__ == '__main__':
    unittest.main()
