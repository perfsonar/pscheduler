#!/usr/bin/env python3
"""
test for the Ipaddr module.
"""

import socket
import unittest
from unittest import mock

from test_base import PschedTestBase

from pscheduler.ipaddr import is_ip, ip_addr_version, ip_normalize_version


def _fake_getaddrinfo(table):
    """
    Build a getaddrinfo() replacement that answers from table, a dict
    mapping a name to a list of addresses in the order returned.
    """
    def fake(host, port, *args, **kwargs):
        if host not in table:
            raise socket.gaierror(socket.EAI_NONAME, 'Name or service not known')
        result = []
        for ip in table[host]:
            if ':' in ip:
                result.append((socket.AF_INET6, socket.SOCK_STREAM, 6, '', (ip, 0, 0, 0)))
            else:
                result.append((socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, 0)))
        return result
    return fake


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

        self.assertEqual(ip_addr_version('::1', ip_version=6), (6, '::1'))
        self.assertEqual(ip_addr_version('::1', ip_version=4), (None, None))

        # By DNS name.  These are guaranteed to be stable as long as
        # nobody breaks the perfsonar.net zone.

        self.assertEqual(ip_addr_version('a1.nv.perfsonar.net', resolve=False), (None, None))
        self.assertEqual(ip_addr_version('aaaa1.nv.perfsonar.net', resolve=False), (None, None))

    def test_ip_normalize_version_first_address(self):
        """Normalize: the first address of each family is used"""

        table = {
            # A host's own name as synthesized by systemd-resolved on a
            # Docker host: the public address first, the docker0 bridge
            # and a link-local IPv6 address after it.
            'node-a.example.net': ['192.0.2.8', '172.17.0.1', 'fe80::fc94:23ff:fe18:6f13'],
            'node-b.example.net': ['198.51.100.7'],
            # Dual-stack names with more than one address per family
            'dual-a.example.net': ['2001:db8::5', 'fe80::1', '2001:db8::6', '192.0.2.8', '192.0.2.9'],
            'dual-b.example.net': ['2001:db8:1::7', '198.51.100.7'],
            # Link-local only, and link-local before a usable address
            'll-a.example.net': ['169.254.10.1'],
            'll-b.example.net': ['169.254.10.2'],
            'mixed.example.net': ['169.254.10.1', '192.0.2.20'],
        }

        with mock.patch('pscheduler.ipaddr.socket.getaddrinfo', _fake_getaddrinfo(table)):

            self.assertEqual(ip_normalize_version('node-a.example.net', 'node-b.example.net'),
                             ('192.0.2.8', '198.51.100.7'))
            self.assertEqual(ip_normalize_version('node-b.example.net', 'node-a.example.net'),
                             ('198.51.100.7', '192.0.2.8'))

            # The IPv6 link-local address of node-a is not used, so IPv6
            # is not chosen even though the other end has IPv6.
            self.assertEqual(ip_normalize_version('node-a.example.net', 'dual-b.example.net'),
                             ('192.0.2.8', '198.51.100.7'))
            self.assertEqual(ip_normalize_version('node-a.example.net', 'dual-b.example.net', ip_version=6),
                             (None, '2001:db8:1::7'))

            self.assertEqual(ip_normalize_version('dual-a.example.net', 'dual-b.example.net'),
                             ('2001:db8::5', '2001:db8:1::7'))
            self.assertEqual(ip_normalize_version('dual-a.example.net', 'dual-b.example.net', ip_version=4),
                             ('192.0.2.8', '198.51.100.7'))

            # Names that resolve only to link-local addresses, e.g. hosts
            # cabled back to back, keep working as before.
            self.assertEqual(ip_normalize_version('ll-a.example.net', 'll-b.example.net'),
                             ('169.254.10.1', '169.254.10.2'))
            # A non-link-local address is preferred even if it comes later.
            self.assertEqual(ip_normalize_version('mixed.example.net', 'node-b.example.net'),
                             ('192.0.2.20', '198.51.100.7'))

            # Unresolvable names
            self.assertEqual(ip_normalize_version('nonexistent.example.net', 'node-b.example.net'),
                             (None, None))

    def test_ip_normalize_version_literals(self):
        """Normalize: literal addresses are used as given"""

        self.assertEqual(ip_normalize_version('192.0.2.8', '198.51.100.7'),
                         ('192.0.2.8', '198.51.100.7'))
        self.assertEqual(ip_normalize_version('2001:db8::5', '2001:db8:1::7'),
                         ('2001:db8::5', '2001:db8:1::7'))
        # A link-local literal is the caller's explicit choice
        self.assertEqual(ip_normalize_version('fe80::1', 'fe80::2', ip_version=6),
                         ('fe80::1', 'fe80::2'))


if __name__ == '__main__':
    unittest.main()
