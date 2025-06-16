#!/usr/bin/env python3
"""
test for the Clockstate module.
"""

import unittest

from test_base import PschedTestBase

from pscheduler.clockstate import clock_state


class TestClockstate(PschedTestBase):
    """
    Clockstate tests.
    """

    def test_clockstate(self):
        """Test clockstate"""

        cstate = clock_state()

        self.assertTrue(isinstance(cstate, dict))
        self.assertTrue("time" in cstate)
        self.assertTrue("synchronized" in cstate)

        if cstate["synchronized"]:

            self.assertTrue("source" in cstate)
            # Offset, reference and error are optional.


if __name__ == '__main__':
    unittest.main()
