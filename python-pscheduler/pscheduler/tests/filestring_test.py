#!/usr/bin/env python3
"""
test for the Filestring module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.filestring import string_from_file


class TestFilestring(PschedTestBase):
    """
    Filestring tests.
    """

    def test_filestring(self):
        """Filestring tests"""

        self.assertRaises(ValueError, string_from_file, 12345)

        self.assertEqual(string_from_file(''), '')

        self.assertEqual(string_from_file("Plain string"), 'Plain string')

        self.assertEqual(string_from_file("\\@literal"), '@literal')
        self.assertEqual(string_from_file("\\@"), '@')

        assert(string_from_file("@/dev/null") == "")
        self.assertRaises(IOError, string_from_file, "@/invalid/path")

        self.assertEqual(string_from_file("  foo  ", strip=False), '  foo  ')
        self.assertEqual(string_from_file("  foo  ", strip=True), 'foo')


if __name__ == '__main__':
    unittest.main()
