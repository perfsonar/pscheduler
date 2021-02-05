#!/usr/bin/env python3
"""
test for the api module.
"""

import unittest

from pscheduler.api import *

from base_test import PschedTestBase


class TestApi(PschedTestBase):
    """
    Api tests.
    """

    def test_api(self):
        """taken from api.__main__"""

        self.assertEqual(
            api_replace_host('https://changedfrom/xxx', 'changedto'),
            'https://changedto/xxx')

        self.assertEqual(
            api_url(host='host.example.com'),
            'https://host.example.com/pscheduler/')
        self.assertEqual(
            api_url(host='host.example.com', path='/both-slash'),
            'https://host.example.com/pscheduler/both-slash')
        self.assertEqual(
            api_url(host='host.example.com', path='both-noslash'),
            'https://host.example.com/pscheduler/both-noslash')

        self.assertEqual(api_host_port(None), (None, None))
        self.assertEqual(api_host_port('foo'), ('foo', None))
        self.assertEqual(api_host_port('foo:1234'), ('foo', 1234))
        self.assertEqual(api_host_port('[::1]'), ('::1', None))
        self.assertEqual(api_host_port('[::1]:1234'), ('::1', 1234))

        self.assertEqual(api_url_hostport(None), 'https://localhost/pscheduler/')
        self.assertEqual(api_url_hostport('foo'), 'https://foo/pscheduler/')
        self.assertEqual(api_url_hostport('foo:1234'), 'https://foo:1234/pscheduler/')
        self.assertEqual(api_url_hostport('[::1]'), 'https://[::1]/pscheduler/')
        self.assertEqual(api_url_hostport('[::1]:1234'), 'https://[::1]:1234/pscheduler/')

        self.assertEqual(api_is_task("https://localhost/pscheduler/tasks/00000000-0000-0000-0000-000000000000"),
                         True)
        self.assertEqual(api_is_task("https://localhost/pscheduler/not-a-task"),
                         False)

        self.assertEqual(api_is_run("https://localhost/pscheduler/tasks/00000000-0000-0000-0000-000000000000/runs/00000000-0000-0000-0000-000000000000"),
                         True)
        self.assertEqual(api_is_run("https://localhost/pscheduler/tasks/00000000-0000-0000-0000-000000000000/runs/not-a-run"),
                         False)


        # TODO: not sure if this is the best test - are there hosts
        # where we know it will be true?
        # self.assertFalse(api_has_pscheduler('localhost'))


if __name__ == '__main__':
    unittest.main()
