"""
tests for the enumerate command
"""

import pscheduler

class EnumerateTest(pscheduler.TestEnumerateUnitTest):
    name = 'throughput'
    scheduling_class='exclusive'
        
if __name__ == '__main__':
    unittest.main()