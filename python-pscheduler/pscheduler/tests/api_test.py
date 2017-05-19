"""
test for the api module.
"""

import unittest

from pscheduler.api import (
    api_url,
    api_has_bwctl,
    api_has_pscheduler,
)

from base_test import PschedTestBase


class TestApi(PschedTestBase):
    """
    Api tests.
    """

    def test_api(self):
        """taken from api.__main__"""

        self.assertEqual(
            api_url(host='host.example.com'),
            'https://host.example.com/pscheduler/')
        self.assertEqual(
            api_url(host='host.example.com', path='/both-slash'),
            'https://host.example.com/pscheduler/both-slash')
        self.assertEqual(
            api_url(host='host.example.com', path='both-noslash'),
            'https://host.example.com/pscheduler/both-noslash')

        # TODO: not sure if this is the best test - are there hosts
        # where we know it will be true?

        # self.assertFalse(api_has_bwctl('localhost'))
        # self.assertFalse(api_has_pscheduler('localhost'))


if __name__ == '__main__':
    unittest.main()
