"""
tests for the enumerate command.
"""

import pscheduler
import unittest

class EnumerateTest(pscheduler.ArchiverEnumerateUnitTest):
    name = 'tcp'
        
if __name__ == '__main__':
    unittest.main()


