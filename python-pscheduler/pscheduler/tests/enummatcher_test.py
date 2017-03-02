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

        # XXX(mmg): There is a new version of this but not sure how it
        # should work.

        # matcher = EnumMatcher({
        #     "enumeration": ["foo", "bar", "biz"],
        # })
        # print matcher

        # print matcher.contains(['foo'])

        pass


if __name__ == '__main__':
    unittest.main()
