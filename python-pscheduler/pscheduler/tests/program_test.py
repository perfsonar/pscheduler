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


    def test_stdout(self):
        status, stdout, stderr = run_program(["printf", "abcd"])
        self.assertEqual(status,0)
        self.assertEqual(stderr, "")
        self.assertEqual(stdout, "abcd")


    def test_stderr(self):
        status, stdout, stderr = run_program(["sh", "-c", "printf 'abcd' 1>&2"])
        self.assertEqual(status,0)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "abcd")


    def test_stdin(self):
        status, stdout, stderr = run_program(["cat"], stdin="abcd")
        self.assertEqual(status,0)
        self.assertEqual(stdout, "abcd")
        self.assertEqual(stderr, "")


    def test_timeout(self):
        status, stdout, stderr = run_program(["sleep", "1"], timeout=0.1)
        self.assertEqual(status,2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Process took too long to run.")


        


if __name__ == '__main__':
    unittest.main()
