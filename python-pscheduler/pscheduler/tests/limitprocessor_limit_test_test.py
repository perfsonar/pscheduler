#!/usr/bin/python3
"""
Test for testlimit
"""

import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.limit.test import *



class TestLimitprocessorLimitTest(PschedTestBase):
    """
    Test the Limit
    """

    # Not testing anything since this limit will be deprecated.



if __name__ == '__main__':
    unittest.main()
