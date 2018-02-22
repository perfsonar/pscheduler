"""
tests for the enumerate command
"""

import pscheduler
import unittest

class EnumerateTest(pscheduler.ToolEnumerateUnitTest):
    name = 'twping'
    tests=['latency']
    preference=0
        
if __name__ == '__main__':
    unittest.main()


