#!/usr/bin/python3
"""
test for the Clockstate module.
"""

import unittest

from base_test import PschedTestBase

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
            # Offset is optional.
            self.assertTrue("reference" in cstate)
            self.assertFalse("error" in cstate)

        else:

            self.assertFalse("source" in cstate)
            self.assertFalse("offset" in cstate)
            self.assertFalse("reference" in cstate)



if __name__ == '__main__':
    unittest.main()
