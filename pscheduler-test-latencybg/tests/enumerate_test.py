"""
tests for the enumerate command
"""

import pscheduler
import unittest

class EnumerateTest(pscheduler.TestEnumerateUnitTest):
    name = 'latencybg'
    scheduling_class='background-multi'
        
if __name__ == '__main__':
    unittest.main()


