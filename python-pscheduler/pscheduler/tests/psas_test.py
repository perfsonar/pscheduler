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
        ips = [
            '8.8.8.8',
            '2607:f8b0:4002:c06::67',
            '198.6.1.1',
            'this-is-not-valid',
        ]

        ret = as_bulk_resolve(ips)

        # Do these only if it looks like anything worked at all.
        # Otherwise, we probably don't have a network connection.

        if filter(lambda key: ret[key] is not None, ret):

            assert(ret.get('this-is-not-valid') is None)
            self.assertEqual(
                ret.get('8.8.8.8'),
                (15169, 'GOOGLE - Google Inc., US'))
            self.assertEqual(
                ret.get('2607:f8b0:4002:c06::67'),
                (15169, 'GOOGLE - Google Inc., US'))
            self.assertEqual(
                ret.get('198.6.1.1'),
                (701, 'UUNET - MCI Communications Services, Inc. d/b/a Verizon Business, US'))


if __name__ == '__main__':
    unittest.main()
