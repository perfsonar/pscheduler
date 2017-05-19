"""
test for the Db module.
"""

import unittest

from base_test import PschedTestBase


class TestDb(PschedTestBase):
    """
    Db tests.
    """

    def test_db(self):
        """Test db"""

        # TODO: probably not a reliable way to test this
        # since there is no one size fits all to connect to
        # a db.
        pass


if __name__ == '__main__':
    unittest.main()
