"""
tests for the data-is-valid command
"""

import pscheduler
import unittest

class DataIsValidTest(pscheduler.ArchiverDataIsValidUnitTest):
    name = 'udp'

    """
    Data validation tests.
    """

    # TODO: Write tests
    def test_schema(self):
        pass


if __name__ == '__main__':
    unittest.main()
