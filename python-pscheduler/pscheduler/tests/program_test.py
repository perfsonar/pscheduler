#!/usr/bin/env python3
"""
test for the Program module.
"""

import unittest
import threading

from base_test import PschedTestBase

from pscheduler.program import *


class TestProgram(PschedTestBase):
    """
    Program tests.
    """

    def test_return_code(self):
        '''
        program = Program(["true"])
        status, stdout, stderr = program.run_program()
        self.assertEqual(status,0)
        
        program = Program(["false"])
        status, stdout, stderr = program.run_program()
        self.assertNotEqual(status,0)
        '''

        program = Program(["true"])
        status, stdout, stderr = program.join()
        self.assertEqual(status,0)

        program = Program(["false"])
        status, stdout, stderr = program.join()
        self.assertNotEqual(status,0)

    def test_stdout(self):
        pass
        '''
        program = Program(["printf", "abcd"])
        status, stdout, stderr = program.run_program()
        self.assertEqual(status,0)
        self.assertEqual(stderr, "")
        self.assertEqual(stdout, "abcd")
        '''

    def test_stderr(self):
        pass
        '''
        program = Program(["sh", "-c", "printf 'abcd' 1>&2"])
        status, stdout, stderr = program.run_program()
        self.assertEqual(status,0)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "abcd")
        '''

    def test_stdin(self):
        pass
        '''
        program = Program(["cat"], stdin="abcd")
        status, stdout, stderr = program.run_program()
        self.assertEqual(status,0)
        self.assertEqual(stdout, "abcd")
        self.assertEqual(stderr, "")
        '''

    def test_timeout(self):
        pass
        '''
        program = Program(["sleep", "1"], timeout=0.1)
        status, stdout, stderr = program.run_program()
        self.assertEqual(status,2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Process took too long to run.")
        '''

    def test_early_terminate(self):
        pass
        '''
        program = Program(["sleep", "2"], timeout=1)
        status, stdout, stderr = program.run_program()
        program.terminate_early()
        self.assertEqual(status,2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Process took too long to run.")
        '''


if __name__ == '__main__':
    unittest.main()

