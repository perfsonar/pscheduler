#!/usr/bin/env python3
"""
test for the Interface module.
"""

import netifaces
import socket
import unittest

from test_base import PschedTestBase

from pscheduler.interface import interface_affinity, source_interface, LocalIPList


class TestInterface(PschedTestBase):
    """
    Interface tests.
    """

    # This is essentially a clean-room re-implementation of what's in
    # the function we're testing.

    # Protocols we care about
    protocols = [ socket.AF_INET, socket.AF_INET6 ]
    addresses = []

    for interface in netifaces.interfaces():
        ifaddresses = netifaces.ifaddresses(interface)
        for protocol in protocols:
            try:
                addresses.append(ifaddresses[protocol][0]['addr'])
            except KeyError:
                pass

    ip_to_test = addresses[0] if len(addresses) > 0 else None

    # The following are wrappers around another library and don't need
    # testing:
    #    source_interface
    #    source_affinity

    def test_local_ip(self):
        """Local ip test"""

        self.assertTrue(self.ip_to_test is not None)
        localips = LocalIPList(refresh=5)
        self.assertTrue(self.ip_to_test in localips)


    def test_source_interface(self):
        """Source interface test"""

        self.assertTrue(self.ip_to_test is not None)
        address, interface = source_interface(self.ip_to_test)
        self.assertEqual(address, self.ip_to_test)
        self.assertNotEqual(interface, None)


if __name__ == '__main__':
    unittest.main()
