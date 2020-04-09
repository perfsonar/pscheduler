#!/usr/bin/env python3
"""
Test for jq limit
"""

import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.limit.jq import *



TEST = {
    "task": {
        "type": "trace",
        "spec": {
            "dest": "foo.bar.org",
            "hops": 2
        }
    }
}



class TestLimitprocessorLimitJQ(PschedTestBase):
    """
    Test the Limit
    """

    def test_data_is_valid(self):
        """Limit Processor / Limit JQ / Data Validation"""

        self.assertEqual(jq_data_is_valid({ "script": "true" }), (True, "OK"))
        self.assertEqual(jq_data_is_valid({}), (False, "At /: 'script' is a required property"))



    def test_limit(self):
        """Limit Processor / Limit JQ / Limit"""

        limit = LimitJQ({ "script": "true" })
        self.assertEqual(limit.evaluate(TEST), {"passed": True})

        limit = LimitJQ({ "script": "false" })
        self.assertEqual(limit.evaluate(TEST),
                         { "passed": False, "reasons": ["Unspecified reason"] })

        limit = LimitJQ({ "script": '"Message"' })
        self.assertEqual(limit.evaluate(TEST),
                         { "passed": False, "reasons": ["Message"] })





if __name__ == '__main__':
    unittest.main()
