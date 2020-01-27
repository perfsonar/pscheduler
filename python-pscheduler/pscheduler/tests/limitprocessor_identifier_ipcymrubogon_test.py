#!/usr/bin/python3
"""
Test for ip-cymru-bogon identifier
"""

import os
import tempfile
import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.identifier.ipcymrubogon import *
from pscheduler.psdns import *


DATA = {
    "exclude": [
        "10.0.0.0/8"
    ],
    "timeout": "PT2S",
    "fail-result": False
}



class TestLimitprocessorIdentifierIPCymruBogon(PschedTestBase):
    """
    Test the Identifier
    """

    def test_data_is_valid(self):
        """Limit Processor / Identifier IP Cymru Bogon / Data Validation"""

        self.assertEqual(data_is_valid(DATA), (True, "OK"))
        self.assertEqual(data_is_valid({}), (False, "At /: 'fail-result' is a required property"))
        self.assertRaises(ValueError, data_is_valid, 123)



    def test_identifier(self):
        """Limit Processor / Identifier IP Cymru Bogon / Identifier"""

        # See if DNS works, bail out if not

        if dns_resolve("perfsonar.net", query="NS") is None:
            print("DNS doesn't appear to work; skipping tests of this module.")
            return

        # See if Team Cymru's DNS service works, bail out if not.

        cymru = dns_resolve("1.1.168.192.bogons.cymru.com")
        if cymru is None:
            print("Bogon service doesn't appear to work; skipping tests of this module.")
            return

        if cymru != "127.0.0.2":
            print("Team Cymru's bogon service returned the wrong result; skipping tests of this module.")
            return


        ident = IdentifierIPCymruBogon(DATA)

        # Trues

        self.assertEqual(
            ident.evaluate({ "requester": "192.168.1.1" }),
            True)

        self.assertEqual(
            ident.evaluate({ "requester": "240.0.0.1" }),
            True)

        self.assertEqual(
            ident.evaluate({ "requester": "1000:dead:beef::1" }),
            True)

        # Falses

        self.assertEqual(
            ident.evaluate({ "requester": "10.9.8.6" }),
            False)

        self.assertEqual(
            ident.evaluate({ "requester": "198.6.1.1" }),
            False)

        self.assertEqual(
            ident.evaluate({ "requester": "128.82.4.1" }),
            False)




if __name__ == '__main__':
    unittest.main()
