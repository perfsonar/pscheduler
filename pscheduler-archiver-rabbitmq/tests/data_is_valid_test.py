"""
tests for the data-is-valid command
"""

import pscheduler
import unittest

class DataIsValidTest(pscheduler.ArchiverDataIsValidUnitTest):
    name = 'rabbitmq'

    """
    Data validation tests.
    """

    def test_schema(self):
        self.assert_cmd('{"schema": 1, "_url": "http://url"}')
        self.assert_cmd('{"schema": 2, "_url": "http://url"}', expected_valid=False)

    def test_url(self):
        self.assert_cmd('{"_url": "http://url"}')
        self.assert_cmd('{}', expected_valid=False)


    def test_exchange(self):
        self.assert_cmd('{"_url": "http://url"}')
        self.assert_cmd('{"_url": "http://url", "exchange": "abcd"}')

    def test_routing_key(self):
        self.assert_cmd('{"_url": "http://url", "routing-key": "abcd"}')

    # NOTE:  Template will be replaced by JQ transforms.

    def test_retry_policy(self):
        self.assert_cmd('{"_url": "http://url", "retry-policy": []', expected_valid=False)
        self.assert_cmd('{"_url": "http://url", "retry-policy": [{"attempts": 3, "wait": "PT1M" }] }}',
                        expected_valid=False)

    def test_additional(self):
        self.assert_cmd('{"_url": "http://url", "invalid-property": 123}', expected_valid=False)



if __name__ == '__main__':
    unittest.main()
