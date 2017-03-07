"""
test for the Stringmatcher module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.stringmatcher import StringMatcher


class TestStringmatcher(PschedTestBase):
    """
    Stringmatcher tests.
    """

    def test_smatcher(self):
        """String matcher test"""
        matcher = StringMatcher({
            "style": "regex",
            "match": "fo+",
            "case-insensitive": False,
            "invert": False
        })

        match_map = {
            'foo': True,
            'bar': False,
            'foobar': True,
            'bazbarfoo': True,
        }

        for k, v in match_map.items():
            self.assertEqual(matcher.matches(k), v)


if __name__ == '__main__':
    unittest.main()
