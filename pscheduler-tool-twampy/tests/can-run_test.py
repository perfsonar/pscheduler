"""
tests for the can-run command
"""

import pscheduler
import unittest

class CanRunTest(pscheduler.ToolCanRunUnitTest):
    name = 'twampy'

    def test_invalid(self):
        #empty
        expected_errors=["Missing test type"]
        self.assert_cmd('{}', expected_valid=False, expected_errors=expected_errors)
        #missing type
        self.assert_cmd(
            '{"spec":{"dest": "10.0.1.1", "schema": 1}}',
            expected_valid=False,
            expected_errors=expected_errors
        )
        #invalid type
        expected_errors=["Unsupported test type"]
        self.assert_cmd(
            '{"type":"foo", "spec":{"dest": "10.0.1.1", "schema": 1}}',
            expected_valid=False,
            expected_errors=expected_errors
        )
        #missing spec
        expected_errors=["Missing test specification"]
        self.assert_cmd(
            '{"type":"latency"}',
            expected_valid=False,
            expected_errors=expected_errors
        )

    def test_valid_latency(self):
        self.assert_cmd('{"type":"latency", "spec":{"dest": "10.0.1.1", "schema": 1}}')

    def test_valid_rtt(self):
        self.assert_cmd('{"type":"rtt", "spec":{"dest": "10.0.1.1", "schema": 1}}')

    def test_valid_stamp_protocol(self):
        self.assert_cmd('{"type":"latency", "spec":{"dest": "10.0.1.1", "schema": 1, "protocol": "stamp"}}')

    def test_valid_twamp_protocol(self):
        self.assert_cmd('{"type":"latency", "spec":{"dest": "10.0.1.1", "schema": 1, "protocol": "twamp"}}')

    def test_invalid_protocol(self):
        self.assert_cmd(
            '{"type":"latency", "spec":{"dest": "10.0.1.1", "schema": 1, "protocol": "icmp"}}',
            expected_valid=False,
        )

    def test_rtt_with_fragment(self):
        # fragmentation control should now be accepted (not rejected by can-run)
        self.assert_cmd('{"type":"rtt", "spec":{"dest": "10.0.1.1", "schema": 1, "fragment": false}}')

if __name__ == '__main__':
    unittest.main()
