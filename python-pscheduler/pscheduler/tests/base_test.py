"""
Base for the unit tests.
"""

import unittest


class PschedTestBase(unittest.TestCase):
    """
    Base class for any shared functionalty for the unit tests.
    """

    def setUp(self):
        """"""
        print "in setup"

    def test_working(self):
        # print 'tests invoked'
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
