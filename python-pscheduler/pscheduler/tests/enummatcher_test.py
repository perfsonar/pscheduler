"""
test for the Enummatcher module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.enummatcher import EnumMatcher


class TestEnummatcher(PschedTestBase):
    """
    Enummatcher tests.
    """

    def test_ematcher(self):
        """Enum matcher tests"""

        # XXX(mmg): This code from the module just throws an exception.
        # revisit.

        # matcher = EnumMatcher({
        #     "enumeration": ["foo", "bar", "biz"],
        #     "invert": False
        # })
        # print matcher

        pass


if __name__ == '__main__':
    unittest.main()
