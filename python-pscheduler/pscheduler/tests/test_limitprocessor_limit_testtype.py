#!/usr/bin/env python3
"""
Test for testtype
"""

import unittest

from test_base import PschedTestBase
from pscheduler.limitprocessor.limit.testtype import *

class TestLimitTestType(PschedTestBase):
    """
    Test for Limit Test Type
    """
    def test_limit_test_type(self):
        limit = LimitTestType({
            "types": [ "rtt", "trace", "latency" ]
        })
        self.assertTrue(limit.evaluate({ "task": {"test": { "type": "rtt" }}}))
        self.assertTrue(limit.evaluate({ "task": {"test": { "type": "trace" }}}))
        self.assertFalse(limit.evaluate({ "task": {"test": { "type": "throughput" }}})["passed"])
        self.assertFalse(limit.evaluate({ "task": {"test": { "type": "bogus" }}})["passed"])
"""
        for test in [ "rtt", "trace", "throughput", "bogus" ]:
            print(test, limit.evaluate({ "task": {
                "test": { "type": test }}
                                     }))
"""

if __name__ == '__main__':
    unittest.main()

