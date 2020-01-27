#!/usr/bin/python3
"""
Test for passfail limit
"""

import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.limit.passfail import *



class TestLimitprocessorLimitPassFail(PschedTestBase):
    """
    Test the Limit
    """

    def test_data_is_valid(self):
        """Limit Processor / Limit PassFail / Data Validation"""

        self.assertEqual(passfail_data_is_valid({ "pass": True }), (True, "OK"))
        self.assertEqual(passfail_data_is_valid({}), (False, "At /: 'pass' is a required property"))



    def test_limit(self):
        """Limit Processor / Limit PassFail / Limit"""

        limit = LimitPassFail({ "pass": True })
        self.assertEqual(limit.evaluate({}), {"passed": True})

        limit = LimitPassFail({ "pass": False })
        self.assertEqual(limit.evaluate({}),
                         { "passed": False, "reasons": [ "Forced failure" ] })




if __name__ == '__main__':
    unittest.main()
