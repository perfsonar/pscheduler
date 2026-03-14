"""
tests for the enumerate command
"""

import pscheduler
import unittest

class EnumerateTest(pscheduler.ToolEnumerateUnitTest):
    name = 'twampy'
    tests=['latency', 'rtt']
    preference=0

if __name__ == '__main__':
    unittest.main()
