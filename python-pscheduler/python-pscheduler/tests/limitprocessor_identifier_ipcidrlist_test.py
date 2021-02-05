#!/usr/bin/env python3
"""
Test for ip-cidr-list identifier
"""

import datetime
import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.identifier.ipcidrlist import *


DATA = {
    "cidrs": [
        "10.0.0.0/8",
        "192.168.1.0/24"
        ]
}


HINTS_HIT = {
    "requester": "10.0.0.1"
}

HINTS_MISS = {
    "requester": "192.168.100.1"
}


class TestLimitprocessorIdentifierAlways(PschedTestBase):
    """
    Test the Identifier
    """

    def test_data_is_valid(self):
        """Limit Processor / Identifier IP CIDR List / Data Validation"""

        self.assertEqual(data_is_valid(DATA), (True, "OK"))
        self.assertEqual(data_is_valid({}), (False, "At /: 'cidrs' is a required property"))
        self.assertRaises(ValueError, data_is_valid, 123)



    def test_identifier(self):
        """Limit Processor / Identifier IP CIDR List / Identifier"""

        ident = IdentifierIPCIDRList(DATA)

        self.assertEqual(ident.evaluate(HINTS_HIT), True)
        self.assertEqual(ident.evaluate(HINTS_MISS), False)





if __name__ == '__main__':
    unittest.main()
