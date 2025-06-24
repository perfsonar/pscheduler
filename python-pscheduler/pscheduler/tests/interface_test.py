#!/usr/bin/env python3
"""
test for the Interface module.
"""

import unittest
import socket

from base_test import PschedTestBase

from pscheduler.interface import interface_affinity, source_interface, LocalIPList


class TestInterface(PschedTestBase):
    """
    Interface tests.
    """

    # Find an IP for localhost, preferring IPv6

    all_ips = filter(
        lambda ip: ip[1] == socket.SocketKind.SOCK_STREAM,
        socket.getaddrinfo('localhost', 0)
    )

    ip_to_test = sorted(
        all_ips,
        key=lambda b: b[0] == socket.AddressFamily.AF_INET
    )[0][4][0]

    # The following are wrappers around another library and don't need
    # testing:
    #    source_interface
    #    source_affinity

    def test_local_ip(self):
        """Local ip test"""
        localips = LocalIPList(refresh=5)
        self.assertTrue(self.ip_to_test in localips)

    def test_source_interface(self):
        """Source interface test"""
        address, interface = source_interface(self.ip_to_test)
        self.assertEqual(address, self.ip_to_test)
        self.assertNotEqual(interface, None)


if __name__ == '__main__':
    unittest.main()
