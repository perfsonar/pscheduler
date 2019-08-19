#!/usr/bin/python3
"""
test for the select module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.psselect import *

class TestPsselect(PschedTestBase):
    """
    Select tests.
    """

    def test_empty(self):
        """All-empty select with a very short timeout"""

        self.assertEqual(
            polled_select([], [], [], 0.0001),
            ([], [], [])
         )


    def test_read(self):
        with open("/dev/null") as fd:
            self.assertEqual(
                polled_select([fd.fileno()], [], [], 2.0),
                ([fd.fileno()], [], [])
            )

    def test_write(self):
        with open("/dev/null", "w") as fd:
            self.assertEqual(
                polled_select([], [fd.fileno()], [], 2.0),
                ([], [fd.fileno()], [])
            )

    def test_except(self):
        self.assertEqual(
            polled_select([], [], [999], 2.0),
            ([], [], [999])
        )


if __name__ == '__main__':
    unittest.main()
