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
        """"""
        self.assertEqual(string_from_file("Plain string"), 'Plain string')

        fstab = string_from_file("@/etc/fstab")

        self.assertGreaterEqual(fstab.find('/etc/fstab'), 0)

        with self.assertRaises(Exception):
            string_from_file("@/invalid/path")


if __name__ == '__main__':
    unittest.main()
