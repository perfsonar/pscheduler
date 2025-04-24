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
        status, stdout, stderr = run_program(["true"])
        self.assertEqual(status,0)

        status, stdout, stderr = run_program(["false"])
        self.assertNotEqual(status,0)

    def test_return_code_class(self):
        program = Program(["true"])
        status, stdout, stderr = program.join()
        self.assertEqual(status,0)

        program = Program(["false"])
        status, stdout, stderr = program.join()
        self.assertNotEqual(status,0)

    def test_stdout(self):
        status, stdout, stderr = run_program(["printf", "abcd"])
        self.assertEqual(status,0)
        self.assertEqual(stderr, "")
        self.assertEqual(stdout, "abcd")

    def test_stdout_class(self):
        program = Program(["printf", "abcd"])
        status, stdout, stderr = program.join()
        self.assertEqual(status,0)
        self.assertEqual(stderr, "")
        self.assertEqual(stdout, "abcd")

    def test_stderr(self):
        status, stdout, stderr = run_program(["sh", "-c", "printf 'abcd' 1>&2"])
        self.assertEqual(status,0)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "abcd")

    def test_stderr_class(self):
        program = Program(["sh", "-c", "printf 'abcd' 1>&2"])
        status, stdout, stderr = program.join()
        self.assertEqual(status,0)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "abcd")

    def test_stdin(self):
        status, stdout, stderr = run_program(["cat"], stdin="abcd")
        self.assertEqual(status,0)
        self.assertEqual(stdout, "abcd")
        self.assertEqual(stderr, "")
    
    def test_stdin_class(self):
        program = Program(["cat"], stdin="abcd")
        status, stdout, stderr = program.join()
        self.assertEqual(status,0)
        self.assertEqual(stdout, "abcd")
        self.assertEqual(stderr, "")

    def test_timeout(self):
        status, stdout, stderr = run_program(["sleep", "1"], timeout=0.1)
        self.assertEqual(status,2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Process took too long to run.")

    def test_timeout_class(self):
        program = Program(["sleep", "1"], timeout=0.1)
        status, stdout, stderr = program.join()
        self.assertEqual(status,2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Process took too long to run.")

    def test_early_terminate_class(self):
        program = Program(["sleep", "30"])
        t = threading.Thread(target=program.join)
        t.start()
        s = program.kill(timeout=0.1)
        print(s)

    def test_line_call_class(self):
        lines = []
        def _line_function(line):
            lines.append(line)
        
        program = Program(["printf", "abcd"], line_call=_line_function)
        status, stdout, stderr = program.join()
        assert status==0
        assert stderr==""
        assert stdout==None
        assert len(lines)==1
        assert lines[0]=="abc"

if __name__ == '__main__':
    unittest.main()

