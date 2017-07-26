"""
test for the Threadsafe module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.threadsafe import ThreadSafeDictionary


class TestThreadsafe(PschedTestBase):
    """
    Threadsafe tests.
    """

    def test_safe_dict(self):
        """Thread safe dict test"""
        tsd = ThreadSafeDictionary()
        tsd['foo'] = 'bar'
        tsd['num'] = 1

        # no use working every __ method but hit a few to get that class
        # into the tests.
        self.assertEqual(tsd.get('foo'), 'bar')
        self.assertTrue(2 > tsd.get('num'))
        self.assertTrue(0 < tsd.get('num'))
        self.assertTrue(1 == tsd.get('num'))


if __name__ == '__main__':
    unittest.main()
