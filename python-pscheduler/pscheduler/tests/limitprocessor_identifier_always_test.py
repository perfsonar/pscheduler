#!/usr/bin/env python3
"""
Test for Always identifier
"""

import datetime
import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.identifier.always import *

class TestLimitprocessorIdentifierAlways(PschedTestBase):
    """
    Test the Identifier
    """

    def test_data_is_valid(self):
        """Limit Processor / Identifier Always / Data Validation"""

        self.assertEqual(data_is_valid({}), (True, "OK"))
        self.assertEqual(data_is_valid(123), (False, 'Data is not an object or not empty.'))


    def test_identifier(self):
        """Limit Processor / Identifier Always / Identifier"""

        ident = IdentifierAlways({})

        self.assertEqual(ident.evaluate({ "requester": "192.168.1.1" }), True)





if __name__ == '__main__':
    unittest.main()
