#!/usr/bin/env python3
"""
test for the Ipaddr module.
"""

import socket
import unittest

from base_test import PschedTestBase

from pscheduler.ipaddr import is_ip, ip_addr_version


class TestIpaddr(PschedTestBase):
    """
    Ipaddr tests.
    """

    def test_is_ip(self):
        """Is-IP Tester"""
        for ip in [ "12.34.56.78", "1234:567::8" ]:
            self.assertTrue(is_ip(ip))
        for ip in [ "foo.bar.org", "perfsonar" ]:
            self.assertFalse(is_ip(ip))
        
    def test_ipaddr(self):
        """IP addr tests"""

        # By Version Number

        self.assertEqual(ip_addr_version('127.0.0.1'), (4, '127.0.0.1'))
        self.assertEqual(ip_addr_version('127.0.0.1', resolve=False), (4, '127.0.0.1'))

        self.assertEqual(ip_addr_version('127.0.0.1/32'), (4, '127.0.0.1'))
        self.assertEqual(ip_addr_version('127.0.0.1/32', resolve=False), (4, '127.0.0.1'))

        self.assertEqual(ip_addr_version('127.0.0.1/quack'), (None, 'Name or service not known'))
        self.assertEqual(ip_addr_version('127.0.0.1/quack', resolve=False), (None, None))

        self.assertEqual(ip_addr_version('::1'), (6, '::1'))
        self.assertEqual(ip_addr_version('::1', resolve=False), (6, '::1'))

        self.assertEqual(ip_addr_version('::1/32'), (6, '::1'))
        self.assertEqual(ip_addr_version('::1/32', resolve=False), (6, '::1'))

        # Different systems come up with different messages, so just check None/not-None
        self.assertEqual(ip_addr_version('::1/quack')[0], None)
        self.assertEqual(ip_addr_version('::1/quack', resolve=False), (None, None))

        # By Address Family

        self.assertEqual(ip_addr_version('127.0.0.1', family=True), (socket.AF_INET, '127.0.0.1'))
        self.assertEqual(ip_addr_version('127.0.0.1', resolve=False, family=True), (socket.AF_INET, '127.0.0.1'))

        self.assertEqual(ip_addr_version('127.0.0.1/32', family=True), (socket.AF_INET, '127.0.0.1'))
        self.assertEqual(ip_addr_version('127.0.0.1/32', resolve=False, family=True), (socket.AF_INET, '127.0.0.1'))

        self.assertEqual(ip_addr_version('127.0.0.1/quack', family=True),(None, 'Name or service not known'))
        self.assertEqual(ip_addr_version('127.0.0.1/quack', resolve=False, family=True), (None, None))

        self.assertEqual(ip_addr_version('::1', family=True), (socket.AF_INET6, '::1'))
        self.assertEqual(ip_addr_version('::1', resolve=False, family=True), (socket.AF_INET6, '::1'))

        self.assertEqual(ip_addr_version('::1/32', family=True), (socket.AF_INET6, '::1'))
        self.assertEqual(ip_addr_version('::1/32', resolve=False, family=True), (socket.AF_INET6, '::1'))

        # Different systems come up with different messages, so just check None/not-None
        self.assertEqual(ip_addr_version('::1/quack', family=True)[0],None)
        self.assertEqual(ip_addr_version('::1/quack', resolve=False, family=True), (None, None))

        # Restricted to one version of an IP or another

        self.assertRaises(AssertionError, ip_addr_version, '127.0.0.1', ip_version=99)

        self.assertEqual(ip_addr_version('127.0.0.1', ip_version=4), (4, '127.0.0.1'))
        self.assertEqual(ip_addr_version('127.0.0.1', ip_version=6), (None, None))
        self.assertEqual(ip_addr_version('a1.nv.perfsonar.net', ip_version=4), (4, '127.0.0.1'))
        self.assertEqual(ip_addr_version('a1.nv.perfsonar.net', ip_version=6), (None, None))

        self.assertEqual(ip_addr_version('::1', ip_version=6), (6, '::1'))
        self.assertEqual(ip_addr_version('::1', ip_version=4), (None, None))
        self.assertEqual(ip_addr_version('aaaa1.nv.perfsonar.net', ip_version=6), (6, 'fc00::1'))
        self.assertEqual(ip_addr_version('aaaa1.nv.perfsonar.net', ip_version=4), (None, None))

        # By DNS name.  These are guaranteed to be stable as long as
        # nobody breaks the perfsonar.net zone.

        self.assertEqual(ip_addr_version('a1.nv.perfsonar.net'), (4, '127.0.0.1'))
        self.assertEqual(ip_addr_version('a1.nv.perfsonar.net', resolve=False), (None, None))

        self.assertEqual(ip_addr_version('aaaa1.nv.perfsonar.net'), (6, 'fc00::1'))
        self.assertEqual(ip_addr_version('aaaa1.nv.perfsonar.net', resolve=False), (None, None))

        # Note that we can't test a-aaaa1.nv because we don't know
        # what the local system will prefer.


if __name__ == '__main__':
    unittest.main()
