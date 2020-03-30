#!/usr/bin/env python3
"""
Test for local-subnet identifier
"""

import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.identifier.localsubnet import *


DATA = {
}



class TestLimitprocessorIdentifierLocalSubnet(PschedTestBase):
    """
    Test the Identifier
    """

    def test_data_is_valid(self):
        """Limit Processor / Identifier Local Subnet / Data Validation"""

        self.assertEqual(data_is_valid(DATA), (True, "OK"))
        self.assertEqual(data_is_valid({ "abc": 123 }),
                         (False, 'Data is not an object or not empty.'))


    def test_identifier(self):
        """Limit Processor / Identifier Local Subnet / Identifier"""

        ident = IdentifierLocalSubnet(DATA)

        self.assertEqual(
            ident.evaluate({ "requester": "127.0.0.5" }),
            True)

        self.assertEqual(
            ident.evaluate({ "requester": "fe80::1" }),
            True)

        self.assertEqual(
            ident.evaluate({ "requester": "192.0.2.9" }),
            False)

        self.assertEqual(
            ident.evaluate({ "requester": "2001:db8::1" }),
            False)




if __name__ == '__main__':
    unittest.main()
