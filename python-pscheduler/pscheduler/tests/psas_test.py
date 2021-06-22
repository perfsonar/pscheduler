#!/usr/bin/env python3
"""
test for the Psas module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.psas import as_bulk_resolve


class TestPsas(PschedTestBase):
    """
    Psas tests.
    """


    def test_bulk_resolve(self):
        """Bulk resolve test"""

        # TODO: These can't be tested reliably because some build
        # locales have unreliable DNS.  It has been thoroughly tested
        # and is believed working.
        return

        ips = [
            '8.8.8.8',
            '2607:f8b0:4002:c06::67',
            '198.6.1.1',
            'this-is-not-valid',
        ]

        ret = as_bulk_resolve(ips)

        # Do these only if it looks like anything worked at all.
        # Otherwise, we probably don't have a network connection.

        assert(ret.get('this-is-not-valid') is None)

        # TODO: These aren't going to be stable forever.
        if False:
            if [key for key in ret if ret[key] is not None]:

                self.assertEqual(
                    ret.get('8.8.8.8')[0],
                    15169, 'GOOGLE, US')
                self.assertEqual(
                    ret.get('2607:f8b0:4002:c06::67')[0],
                    15169)
                self.assertEqual(
                    ret.get('198.6.1.1')[0],
                    701)


if __name__ == '__main__':
    unittest.main()
