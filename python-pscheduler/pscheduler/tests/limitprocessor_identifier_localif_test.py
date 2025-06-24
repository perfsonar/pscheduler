#!/usr/bin/env python3
"""
Test for localif identifier
"""

import unittest
import socket

from base_test import PschedTestBase

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

        # Find an IP for localhost, preferring IPv6

        all_ips = filter(
            lambda ip: ip[1] == socket.SocketKind.SOCK_STREAM,
            socket.getaddrinfo('localhost', 0)
        )

        local_ip = sorted(
            all_ips,
            key=lambda b: b[0] == socket.AddressFamily.AF_INET
        )[0][4][0]

        self.assertEqual(ident.evaluate({ "requester": local_ip }), True)


if __name__ == '__main__':
    unittest.main()
