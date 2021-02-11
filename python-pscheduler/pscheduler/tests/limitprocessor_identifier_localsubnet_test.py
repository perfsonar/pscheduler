#!/usr/bin/env python3
"""
Test for local-subnet identifier
"""

import unittest
import netifaces

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

        test_ifaces = {
            "lo0": {
                netifaces.AF_INET: [
                    {'addr': '127.0.0.1', 'netmask': '255.0.0.0', 'peer': '127.0.0.1'}
                ],
                netifaces.AF_INET6: [
                    {'addr': '::1', 'netmask': 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128', 'peer': '::1', 'flags': 0}, 
                    {'addr': 'fe80::1%lo0', 'netmask': 'ffff:ffff:ffff:ffff::/64', 'flags': 0}
                ]
            }
        }

        ident = IdentifierLocalSubnet(DATA, test_ifaces=test_ifaces)

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
