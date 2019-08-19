#!/usr/bin/env python3
"""
test for the Program module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.program import run_program


class TestProgram(PschedTestBase):
    """
    Program tests.
    """

    def test_return_code(self):
        """"""
        status, stdout, stderr = run_program(["true"])
        self.assertEqual(status,0)

        status, stdout, stderr = run_program(["false"])
        self.assertNotEqual(status,0)


        


if __name__ == '__main__':
    unittest.main()
