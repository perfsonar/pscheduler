#!/usr/bin/env python3
"""
Tests for LimitSet
"""

import unittest
import pscheduler

from test_base import PschedTestBase
from pscheduler.limitprocessor.limitset import *

class TestLimitSet(PschedTestBase):
    """
    Test for LimitSet
    """
    
    thelimits = [
        {
            "name": "always",
            "description": "Always passes",
            "type": "pass-fail",
            "data": {
                "pass": True
            }
        },
        {
            "name": "never",
            "description": "Always fails",
            "clone": "always",
            "data": {
                "pass": False
            }
        },
        {
            "name": "lunchtime",
            "description": "Never at noon",
            "type": "run-schedule",
            "data": {
                "hour": [ 12 ],
                "overlap": True
            }
        },
        {
            "name": "century20",
            "description": "The 20th century",
            "type": "run-daterange",
            "data": {
                "start": "1901-01-01T00:00:00",
                "end": "2001-01-01T00:00:00"
            }
        },
        {
            "name": "century21",
            "description": "The 21st century",
            "type": "run-daterange",
            "data": {
                "start": "2001-01-01T00:00:00",
                "end": "2101-01-01T00:00:00"
            }
        },
        {
            "name": "innocuous-tests",
            "description": "Tests that are harmless",
            "type": "test-type",
            "data": {
                "types": [ "rtt", "latency", "trace" ]
            }
        },
        {
            "name": "innocuous-tests-inv",
            "description": "Tests that are harmful",
            "type": "test-type",
            "data": {
                "types": [ "rtt", "latency", "trace" ]
            },
            "invert": True
        },
    ]

    def test_limit_set(self):
        theset = LimitSet(self.thelimits)

        # This is test code that doesn't interact with the network, so
        # hard-wired IPv4s are fine here.
        hints = {
            "requester": "127.0.0.1",
            "server": "127.0.0.1",
            "protocol": "https"
        }

        task = {
            "type": "idle",
            "spec": {
                "schema": 1,
                "duration": "PT10S"
            },
            "run_schedule": {
                "start": "2016-01-01T11:50:00",
                "duration": "PT10S"
            }
        }

        proposal = {
            "hints": hints,
            "task": task
        }
        
        results = []

        for limit in self.thelimits:
            results.append(theset.check(proposal, limit['name'], True)['passed'])
        
        self.assertEqual(results, [True, False, False, False, True, False, True])

if __name__ == '__main__':
    unittest.main()

