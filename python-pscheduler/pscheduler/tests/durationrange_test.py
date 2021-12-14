#!/usr/bin/env python3
"""
test for the Durationrange module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.durationrange import DurationRange


class TestDurationrange(PschedTestBase):
    """
    Durationrange tests.
    """

    def test_drange(self):
        """Duration range tests"""

        drange = DurationRange({
            "lower": "PT10S",
            "upper": "PT1M"
        })

        value = 'PT1S'
        result = value in drange

        self.assertFalse(result)
        self.assertEqual(drange.contains(value), (False, 'not in PT10S..PT1M'))
        self.assertEqual(drange.contains(value, invert=True), (True, None))

        value = 'PT30S'
        result = value in drange

        self.assertTrue(result)
        self.assertEqual(drange.contains(value), (True, None))
        self.assertEqual(drange.contains(value, invert=True), (False, 'not outside PT10S..PT1M'))

        value = 'PT5M'
        result = value in drange

        self.assertFalse(result)
        self.assertEqual(drange.contains(value), (False, 'not in PT10S..PT1M'))
        self.assertEqual(drange.contains(value, invert=True), (True, None))


if __name__ == '__main__':
    unittest.main()
