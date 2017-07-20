"""
test for the Psjson module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.psjson import (
    json_decomment,
    json_dump,
    json_load,
    json_substitute,
)


class TestPsjson(PschedTestBase):
    """
    Psjson tests.
    """

    def test_jsondecomment(self):
        """Test decomment"""
        doc = dict(foo='foo')
        doc['#bar'] = 'bar'

        ret = json_decomment(doc)
        # prefix removed
        self.assertEqual(ret, dict(foo='foo'))

    def test_sub(self):
        """Test substitute"""
        doc = dict(foo='foo')

        ret = json_substitute(doc, 'foo', 'bar')

        # value swapped
        self.assertEqual(ret, dict(foo='bar'))

    def test_load(self):
        """Test loading"""

        dstring = '{"foo": "bar"}'

        ret = json_load(dstring)
        self.assertEqual(ret, dict(foo='bar'))

        dstring += 'xxxx'

        # bad value
        self.assertRaises(ValueError, json_load, dstring)

    def test_dump(self):
        doc = dict(foo='foo')

        ret = json_dump(doc)
        self.assertEqual(ret, '{"foo": "foo"}')


if __name__ == '__main__':
    unittest.main()
