#!/usr/bin/env python3
"""
test for the JQFilter module.
"""

import sys
import unittest

from base_test import PschedTestBase

from pscheduler.jqfilter import JQFilter


class TestJQFilter(PschedTestBase):
    """
    JQFilter tests.
    """

    def test_string(self):
        """Test a string filter"""

        f = JQFilter(".")
        self.assertEqual(f({"abc": 123})[0], {"abc": 123 })


    def test_array(self):
        """Test an array filter"""

        f = JQFilter([ "", ".", "", ""])
        self.assertEqual(f({"abc": 123})[0], {"abc": 123 })


    def test_array_empty(self):
        """Test an empty array filter"""

        f = JQFilter([])
        self.assertEqual(f({"abc": 123})[0], {"abc": 123 })


    def test_hash(self):
        """Test a hash filter"""

        f = JQFilter({"script": "."})
        self.assertEqual(f({"abc": 123})[0], {"abc": 123 })


    def test_hash_array(self):
        """Test a hash filter with an array script"""

        f = JQFilter({"script": [ "", ".", "", ""]})
        self.assertEqual(f({"abc": 123})[0], {"abc": 123 })


    def test_args_empty(self):
        f = JQFilter({"script": "."}, args={})
        self.assertEqual(f(123)[0], 123)

    def test_args(self):
        f = JQFilter({"script": "$value"}, args={"value": 123})
        self.assertEqual(f(None)[0], 123)

    # TODO: Need a way to test groomed filters without depending on
    # anything else being installed.  Might not be doable.

    def test_wrong_type(self):
        """Test a wrongly-typed filter"""
        with self.assertRaises(ValueError):
            f = JQFilter(1234)


    def test_bad_syntax(self):
        """Test a filter with the wrong syntax"""

        with self.assertRaises(ValueError):
            f = JQFilter("this is bad")

if __name__ == '__main__':
    unittest.main()
