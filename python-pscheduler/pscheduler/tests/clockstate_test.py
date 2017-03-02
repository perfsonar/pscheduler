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

        # XXX(mmg): not sure how to properly test this other
        # than simple a simple regression/coverage check.
        cstate = clock_state()
        self.assertTrue(isinstance(cstate, dict))
        self.assertEqual(set(cstate.keys()), set(['synchronized', 'time']))


if __name__ == '__main__':
    unittest.main()
