"""
test for the Ipaddr module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.ipaddr import ip_addr_version


class TestIpaddr(PschedTestBase):
    """
    Ipaddr tests.
    """

    def test_ipaddr(self):
        """IP addr tests"""

        self.assertEqual(ip_addr_version('127.0.0.1'), (4, '127.0.0.1'))
        self.assertEqual(ip_addr_version('127.0.0.1', resolve=False), (4, '127.0.0.1'))

        self.assertEqual(ip_addr_version('127.0.0.1/32'), (4, '127.0.0.1'))
        self.assertEqual(ip_addr_version('127.0.0.1/32', resolve=False), (4, '127.0.0.1'))

        self.assertEqual(ip_addr_version('127.0.0.1/quack'), (None, None))
        self.assertEqual(ip_addr_version('127.0.0.1/quack', resolve=False), (None, None))

        self.assertEqual(ip_addr_version('::1'), (6, '::1'))
        self.assertEqual(ip_addr_version('::1', resolve=False), (6, '::1'))

        self.assertEqual(ip_addr_version('::1/32'), (6, '::1'))
        self.assertEqual(ip_addr_version('::1/32', resolve=False), (6, '::1'))

        self.assertEqual(ip_addr_version('::1/quack'), (None, None))
        self.assertEqual(ip_addr_version('::1/quack', resolve=False), (None, None))

        # TODO: are the following resolved tests subject to breakage due
        # to changing IP addresses? If so, do what?

        # TODO: these appear to be unstable, get clarity.

        # self.assertEqual(ip_addr_version('www.perfsonar.net'), (4, '207.75.164.248'))
        # self.assertEqual(ip_addr_version('www.perfsonar.net', resolve=False), (None, None))

        # self.assertEqual(ip_addr_version('ipv4.test-ipv6.com'), (4, '216.218.228.125'))
        # self.assertEqual(ip_addr_version('ipv4.test-ipv6.com', resolve=False), (None, None))

        # self.assertEqual(ip_addr_version('ipv6.test-ipv6.com'), (6, '2001:470:1:18::125'))
        # self.assertEqual(ip_addr_version('ipv6.test-ipv6.com', resolve=False), (None, None))


if __name__ == '__main__':
    unittest.main()
