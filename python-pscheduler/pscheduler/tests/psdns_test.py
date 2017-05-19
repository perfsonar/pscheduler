"""
test for the Psdns module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.psdns import dns_resolve, dns_bulk_resolve


class TestPsdns(PschedTestBase):
    """
    Psdns tests.
    """

    def test_resolve(self):
        """Resolve test"""

        self.assertEqual(dns_resolve('localhost'), '127.0.0.1')

        # TODO: Figure out how to determine if we have network and
        # therefore DNS
        #self.assertEqual(dns_resolve('google-public-dns-a.google.com'), '8.8.8.8')
        ## TODO: are the following checks stable?
        #self.assertEqual(
        #    dns_resolve('www.perfsonar.net', ip_version=6), '2001:48a8:68fe::248')

    def test_bulk_resolve(self):
        """Bulk resolve test."""

        ret = dns_bulk_resolve([
            'www.perfsonar.net',
            'www.es.net',
            'www.geant.org',
            'www.iu.edu',
            'www.internet2.edu',
            'does-not-exist.internet2.edu',
            'google-public-dns-a.google.com',
        ], ip_version=4)

        # If none of these resolved, we probably don't have network or
        # DNS is severely broken.
        have_network = len(filter(lambda key: ret[key] is not None, ret)) > 0

        if have_network:
            # these should be stable
            self.assertIsNone(ret.get('does-not-exist.internet2.edu'))
            self.assertEqual(ret.get('google-public-dns-a.google.com'), '8.8.8.8')

        # ipv6

        if have_network:
            ret = dns_bulk_resolve([
                'www.perfsonar.net',
            ], ip_version=6)

            self.assertEqual(ret.get('www.perfsonar.net'), '2001:48a8:68fe::248')

        # reverse

        if have_network:
            ret = dns_bulk_resolve([
                '192.168.12.34',
                '8.8.8.8',
                '198.6.1.1',
                '8.8.8.0',
                '2607:f8b0:4002:c06::67',
                'this-is-not-valid'
            ], reverse=True)

            self.assertIsNone(ret.get('this-is-not-valid'))
            self.assertEqual(ret.get('8.8.8.8'), 'google-public-dns-a.google.com')

        # bulk none - empty dict
        self.assertEqual(dns_bulk_resolve([]), dict())


if __name__ == '__main__':
    unittest.main()
