#!/usr/bin/env python3

import unittest

from test_base import PschedTestBase

import pscheduler

class TestIPCIDRMatcher(PschedTestBase):
    """
    Tests for ipcidrmatcher.py
    """

    def test_IPCIDRMatcher(self):
        cidrs = ["192.168.1.0/24", "10.0.0.0/8"]

        matcher = pscheduler.IPCIDRMatcher({
            "cidr": cidrs,
            "invert": False
        })

        self.assertTrue(matcher.contains("192.168.1.1"))
        self.assertTrue(matcher.contains("192.168.1.234"))
        self.assertFalse(matcher.contains("192.168.2.1"))
        self.assertFalse(matcher.contains("1.2.3.4"))
        self.assertTrue(matcher.contains("10.16.57.254"))
        self.assertTrue(matcher.contains("10.0.0.1"))


if __name__ == '__main__':
    unittest.main()
