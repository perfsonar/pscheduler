#!/usr/bin/env python3
"""
Test for ip-reverse-dns identifier
"""

import os
import tempfile
import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.identifier.ipreversedns import *
from pscheduler.psdns import *


# TODO: This depends on the continued existence of a couple of well-known hosts.

DATA = {
    "match": {
        "style": "regex",
        "match": "^(dns\\.google|one\\.one\\.one\\.one)$"
    },
    "timeout": "PT5S"
}



class TestLimitprocessorIdentifierIPReverseDNS(PschedTestBase):
    """
    Test the Identifier
    """

    def test_data_is_valid(self):
        """Limit Processor / Identifier IP Reverse DNS / Data Validation"""

        self.assertEqual(data_is_valid(DATA), (True, "OK"))
        self.assertEqual(data_is_valid({}), (False, "At /: 'match' is a required property"))
        self.assertRaises(ValueError, data_is_valid, 123)



    def test_identifier(self):
        """Limit Processor / Identifier IP Reverse DNS / Identifier"""

        # TODO: These can't be tested reliably because some build
        # locales have unreliable DNS.  It has been thoroughly tested
        # and is believed working.
        return

        # See if DNS works, bail out if not

        if dns_resolve("perfsonar.net", query="NS") is None:
            print("DNS doesn't appear to work; skipping tests of this module.")
            return

        ident = IdentifierIPReverseDNS(DATA)

        # Trues

        self.assertEqual(
            ident.evaluate({ "requester": "8.8.8.8" }),
            True)

        self.assertEqual(
            ident.evaluate({ "requester": "1.1.1.1" }),
            True)

        # Falses

        self.assertEqual(
            ident.evaluate({ "requester": "192.0.2.1" }),
            False)

        self.assertEqual(
            ident.evaluate({ "requester": "198.51.100.1" }),
            False)




if __name__ == '__main__':
    unittest.main()
