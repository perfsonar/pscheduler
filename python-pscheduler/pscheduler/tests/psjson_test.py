#!/usr/bin/env python3
"""
test for the Psjson module.
"""

import io
import os
import tempfile
import unittest

from base_test import PschedTestBase

from pscheduler.psjson import *


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

    def test_file(self):
        """Test loading from a file"""

        # PORT: Unix only
        with open("/dev/null", "r") as infile:
            # All we care is that it doesn't like the input.
            self.assertRaises(ValueError, json_load, infile)



    def test_dump(self):
        doc = dict(foo='foo')

        ret = json_dump(doc)
        self.assertEqual(ret, '{"foo":"foo"}')


    #
    # JSON Streaming Classes
    #

    def test_RFC7464_emitter(self):
        buf = io.StringIO()
        emitter = RFC7464Emitter(buf)
        emitter({"foo": 123})
        emitter({"bar": 123})
        self.assertEqual(buf.getvalue(),
                         '\x1e{"foo":123}\n\x1e{"bar":123}\n')


    def test_RFC7464_parser(self):

        buf=io.StringIO('\x1e{"foo": 123}\nXYZZY\n')
        parser = RFC7464Parser(buf)

        # First line is valid
        self.assertEqual(parser(),  {"foo": 123})

        # Second line is bogus
        self.assertRaises(ValueError, parser)



if __name__ == '__main__':
    unittest.main()
