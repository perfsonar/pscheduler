#!/usr/bin/env python3
"""
Test for ip-cidr-list-url identifier
"""

import os
import tempfile
import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.identifier.ipcidrlisturl import *

CIDR_LIST = """
128.82.0.0/16
198.6.1.0/24
10.10.10.0/24
"""

DATA = {
    "source": "https://this-will-be-filled-in-later",
    "exclude": [
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16"
    ],
    "update": "PT5S",
    "retry": "PT1M",
    "fail-state": False
}



class TestLimitprocessorIdentifierIPCIDRListURL(PschedTestBase):
    """
    Test the Identifier
    """

    def test_data_is_valid(self):
        """Limit Processor / Identifier IP CIDR List URL / Data Validation"""

        self.assertEqual(data_is_valid(DATA), (True, "OK"))
        self.assertEqual(data_is_valid({}), (False, "At /: 'source' is a required property"))
        self.assertRaises(ValueError, data_is_valid, 123)



    def test_identifier(self):
        """Limit Processor / Identifier IP CIDR List / Identifier"""

        with tempfile.NamedTemporaryFile() as listfile:

            listfile.write(bytes(CIDR_LIST, "ascii"))
            listfile.flush()

            DATA["source"] = "file://" + listfile.name

            ident = IdentifierIPCIDRListURL(DATA)

            # In list
            self.assertEqual(
                ident.evaluate({ "requester": "128.82.4.1" }),
                True)

            # In list but excluded
            self.assertEqual(
                ident.evaluate({ "requester": "10.10.10.10" }),
                False)

            # Not in list
            self.assertEqual(
                ident.evaluate({ "requester": "8.8.8.8" }),
                False)

            # Not in list but excluded
            self.assertEqual(
                ident.evaluate({ "requester": "10.0.0.1" }),
                False)

            # Invalid IP
            self.assertRaises(ValueError,
                              ident.evaluate,
                              { "requester": "kaboom" })






if __name__ == '__main__':
    unittest.main()
