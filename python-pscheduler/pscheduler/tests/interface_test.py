#!/usr/bin/env python3
"""
test for the Interface module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.interface import interface_affinity, source_interface, LocalIPList


class TestInterface(PschedTestBase):
    """
    Interface tests.
    """

    # The following are wrappers around another library and don't need
    # testing:
    #    source_interface
    #    source_affinity

    def test_local_ip(self):
        """Local ip test"""
        localips = LocalIPList(refresh=5)

        self.assertTrue('127.0.0.1' in localips)

    def test_source_interface(self):
        """Source interface test"""
        ip = '127.0.0.1'
        address, interface = source_interface(ip)
        self.assertEqual(address, ip)
        self.assertNotEqual(interface, None)


if __name__ == '__main__':
    unittest.main()
