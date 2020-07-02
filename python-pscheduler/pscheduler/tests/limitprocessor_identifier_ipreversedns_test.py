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


DATA = {
    "match": {
        "style": "regex",
        "match": "^(ntp[0-9]*\\.internet2\\.edu|chronos\\.es\\.net|saturn\\.es\\.net)$"
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

        # See if DNS works, bail out if not

        if dns_resolve("perfsonar.net", query="NS") is None:
            print("DNS doesn't appear to work; skipping tests of this module.")
            return

        ident = IdentifierIPReverseDNS(DATA)

        # Trues

        # ntp0.internet2.edu
        self.assertEqual(
            ident.evaluate({ "requester": "207.75.164.18" }),
            True)

        # {chronos,saturn}.es.net
        self.assertEqual(
            ident.evaluate({ "requester": "198.124.252.90" }),
            True)

        # Falses

        # webprod2.internet2.edu (RRs to internet2.edu)
        self.assertEqual(
            ident.evaluate({ "requester": "207.75.164.248" }),
            False)

        # www.internet2.edu
        self.assertEqual(
            ident.evaluate({ "requester": "2001:48a8:68fe::248" }),
            False)




if __name__ == '__main__':
    unittest.main()
