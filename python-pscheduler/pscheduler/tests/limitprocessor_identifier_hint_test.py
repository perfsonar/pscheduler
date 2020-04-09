#!/usr/bin/env python3
"""
Test for Hintidentifier
"""

import datetime
import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.identifier.hint import *


DATA = {
    "hint": "value",
    "match": {
        "style": "exact",
        "match": "testing",
        "case-insensitive": False
    }
}

HINTS_HIT = {
    "value": "testing"
}

HINTS_MISS = {
    "value": "not-testing"
}


class TestLimitprocessorIdentifierAlways(PschedTestBase):
    """
    Test the Identifier
    """

    def test_data_is_valid(self):
        """Limit Processor / Identifier Hint / Data Validation"""

        self.assertEqual(data_is_valid(DATA), (True, "OK"))
        self.assertEqual(data_is_valid({}), (False, "At /: 'hint' is a required property"))
        self.assertRaises(ValueError, data_is_valid, 123)



    def test_identifier(self):
        """Limit Processor / Identifier Hint / Identifier"""

        ident = IdentifierHint(DATA)

        self.assertEqual(ident.evaluate(HINTS_HIT), True)
        self.assertEqual(ident.evaluate(HINTS_MISS), False)





if __name__ == '__main__':
    unittest.main()
