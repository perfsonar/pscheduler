#!/usr/bin/python3
"""
Test for localif identifier
"""

import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.identifier.localif import *


DATA = {
}


class TestLimitprocessorIdentifierJQ(PschedTestBase):
    """
    Test the Identifier
    """

    def test_data_is_valid(self):
        """Limit Processor / Identifier Local Interface / Data Validation"""

        self.assertEqual(data_is_valid(DATA), (True, "OK"))
        self.assertEqual(data_is_valid({ "abc": 123 }),
                         (False, 'Data is not an object or not empty.'))


    def test_identifier(self):
        """Limit Processor / Identifier Local Interface / Identifier"""

        ident = IdentifierLocalIF(DATA)

        self.assertEqual(ident.evaluate({ "requester": "192.168.1.1" }), False)
        self.assertEqual(ident.evaluate({ "requester": "127.0.0.1" }), True)



if __name__ == '__main__':
    unittest.main()
