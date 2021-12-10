#!/usr/bin/env python3
"""
test for the psurl module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.psurl import *


class TestPsurl(PschedTestBase):
    """
    URL tests.
    """

    def test_url_bad(self):
        """IP addr tests"""

        # Missing scheme

        no_scheme = "no-scheme"

        (status, _) = url_get(no_scheme, json=False, throw=False)
        self.assertEqual(status, 400)

        self.assertRaises(URLException, url_get, no_scheme, json=False, throw=True)


        # Bad IPv6 address

        bad6 = "http://dead:beef::1bad:cafe/"

        (status, _) = url_get(bad6, json=False, throw=False)
        self.assertEqual(status, 400)

        self.assertRaises(URLException, url_get, bad6, json=False, throw=True)


        # This address is in the blocks reserved for RFC6666 discards.
        discard = "https://[0100::0010]/"

        self.assertEqual(
            url_get(discard, timeout=1, json=False, throw=False)[0], 400)
        self.assertRaises(URLException, url_get, discard, json=False, timeout=1, throw=True)



    def test_url_get(self):
        # TODO: Would need a web server to test this
        pass


    def test_url_get_bind(self):
        """See if binding works"""
        self.assertEqual(
            url_get("http://127.0.0.1", bind="192.0.2.1", throw=False),
            (400, 'bind failed with errno 99: Cannot assign requested address')
        )

        # This returns varied error strings; we just care that the beginning is right.
        (status, message) = url_get("http://not.a.valid.host", bind="127.0.0.1", throw=False)
        self.assertEqual(
            (status, message.startswith("Could not resolve host:")),
            (400, True)
        )


    def test_url_put(self):
        # TODO: Would need a web server to test this
        pass

    def test_url_post(self):
        # TODO: Would need a web server to test this
        pass

    def test_url_delete(self):
        # TODO: Would need a web server to test this
        pass


if __name__ == '__main__':
    unittest.main()
