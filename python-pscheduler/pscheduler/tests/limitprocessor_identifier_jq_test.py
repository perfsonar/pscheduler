#!/usr/bin/env python3
"""
Test for jq identifier
"""

import os
import tempfile
import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.identifier.jq import *


DATA = {
    "script": 'true'
}



class TestLimitprocessorIdentifierJQ(PschedTestBase):
    """
    Test the Identifier
    """

    def test_data_is_valid(self):
        """Limit Processor / Identifier JQ / Data Validation"""

        self.assertEqual(data_is_valid(DATA), (True, "OK"))
        self.assertEqual(data_is_valid({}), (False, "At /: 'script' is a required property"))
        self.assertRaises(ValueError, data_is_valid, 123)



    def test_identifier(self):
        """Limit Processor / Identifier JQ / Identifier"""

        ident = IdentifierJQ(DATA)

        self.assertEqual(ident.evaluate({ "requester": "192.168.1.1" }), True)



if __name__ == '__main__':
    unittest.main()
