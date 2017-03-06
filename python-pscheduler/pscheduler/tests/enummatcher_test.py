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

        matcher = EnumMatcher({
            "enumeration": ["foo", "bar", "biz"],
        })

        self.assertTrue(matcher.contains(['foo']))
        self.assertTrue(matcher.contains('foo'))
        self.assertTrue(matcher.contains(['foo', 'bar']))
        self.assertFalse(matcher.contains(["foo", "notallowed", "biz"]))

        pass


if __name__ == '__main__':
    unittest.main()
