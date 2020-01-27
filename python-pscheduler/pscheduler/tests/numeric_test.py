#!/usr/bin/python3
"""
test for the Numeric module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.numeric import HighInteger


class TestNumeric(PschedTestBase):
    """
    Numeric tests.
    """

    def test_highinteger(self):
        """Numeric range test"""

        high = HighInteger()
        self.assertTrue(high.value() is None)

        high = HighInteger(1)
        self.assertTrue(high.value() == 1)

        high.set(0)
        self.assertTrue(high.value() == 1)

        high.set(10)
        self.assertTrue(high.value() == 10)

        high.set(5)
        self.assertTrue(high.value() == 10)



if __name__ == '__main__':
    unittest.main()
