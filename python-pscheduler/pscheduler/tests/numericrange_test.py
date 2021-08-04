#!/usr/bin/env python3
"""
test for the Numericrange module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.numericrange import NumericRange


class TestNumericrange(PschedTestBase):
    """
    Numericrange tests.
    """

    def test_nrange(self):
        """Numeric range test"""
        nrange = NumericRange({
            "lower": 3.14,
            "upper": "100K"
        })

        value = 1
        result = value in nrange

        self.assertFalse(result)
        self.assertTrue(nrange.contains(value, invert=True)[0])

        value = 6.78
        result = value in nrange

        self.assertTrue(result)
        self.assertFalse(nrange.contains(value, invert=True)[0])

        value = '10K'
        result = value in nrange

        self.assertTrue(result)
        self.assertFalse(nrange.contains(value, invert=True)[0])

        value = '100K'
        result = value in nrange

        self.assertTrue(result)
        self.assertFalse(nrange.contains(value, invert=True)[0])

        value = '1M'
        result = value in nrange

        self.assertFalse(result)
        self.assertTrue(nrange.contains(value, invert=True)[0])


if __name__ == '__main__':
    unittest.main()
