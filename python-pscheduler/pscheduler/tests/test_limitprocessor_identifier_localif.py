#!/usr/bin/env python3
"""
Test for localif identifier
"""

import unittest
import socket

from test_base import PschedTestBase

from pscheduler.interface import LocalIPList
from pscheduler.limitprocessor.identifier.localif import *


DATA = {
}


class TestLimitprocessorIdentifierJQ(PschedTestBase):
    """
    Test the Identifier
    """

    def test_data_is_valid(self):
        """Limit Processor / Identifier Local Interface / Data Validation"""

        self.assertEqual(data_is_valid(DATA), (True, "OK"))
        self.assertEqual(data_is_valid({ "abc": 123 }),
                         (False, 'Data is not an object or not empty.'))


    def test_identifier(self):
        """Limit Processor / Identifier Local Interface / Identifier"""

        ident = IdentifierLocalIF(DATA)

        self.assertEqual(ident.evaluate({ "requester": "192.168.1.1" }), False)

        local_ips = list(LocalIPList())
        # Very unusual, but you never can tell with IPs.
        self.assertTrue(len(local_ips) > 0)

        # Any local IP will do.
        self.assertEqual(ident.evaluate({ "requester": local_ips[0] }), True)


if __name__ == '__main__':
    unittest.main()
