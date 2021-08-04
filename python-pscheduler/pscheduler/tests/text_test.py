#!/usr/bin/env python3
"""
test for the Text module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.text import prefixed_wrap


class TestText(PschedTestBase):
    """
    Text tests.
    """

    def test_wrap(self):
        """Wrap test"""

        text = """
Sample text
For my test
"""

        ret = prefixed_wrap('pfix:', text)
        self.assertEqual(ret, 'pfix: Sample text For my test')


if __name__ == '__main__':
    unittest.main()
