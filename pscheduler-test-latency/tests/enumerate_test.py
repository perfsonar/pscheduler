"""
tests for the enumerate command
"""

import pscheduler

class EnumerateTest(pscheduler.TestEnumerateUnitTest):
    name = 'latency'
    scheduling_class='normal'
        
if __name__ == '__main__':
    unittest.main()


