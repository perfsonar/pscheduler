#!/usr/bin/env python3
"""
test for the numa module.
"""

import unittest

from pscheduler.numa import *

from base_test import PschedTestBase


class TestNuma(PschedTestBase):
    """
    NUMA tests.
    """

    def test_numa(self):

        # These may or may not work; we just don't want them to crash.

        for node in range(0,3):
            numa_node_ok(node)

        # One bad one.

        self.assertIn(
            numa_node_ok("foo"),
            [(False, "libnuma: Warning: unparseable node description `foo'"),
                (False, 'numactl: This system does not support NUMA policy')]
            )


if __name__ == '__main__':
    unittest.main()
