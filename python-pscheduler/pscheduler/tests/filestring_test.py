#!/usr/bin/python3
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

        self.assertEqual(string_from_file(''), '')

        self.assertEqual(string_from_file("Plain string"), 'Plain string')

        assert(string_from_file("@/dev/null") == "")

        self.assertRaises(Exception, string_from_file, "@/invalid/path")


if __name__ == '__main__':
    unittest.main()
