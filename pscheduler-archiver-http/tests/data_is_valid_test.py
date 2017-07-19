"""
tests for the data-is-valid command
"""

import pscheduler
import unittest

class DataIsValidTest(pscheduler.ArchiverDataIsValidUnitTest):
    name = 'http'

    """
    Data validation tests.
    """


    def test_schema(self):
        self.assert_cmd('{"_url": "http://test"}')
        self.assert_cmd('{"schema": 1, "_url": "http://test"}')
        self.assert_cmd('{"schema": 2, "_url": "http://test"}', expected_valid=False)


    def test_url(self):
        self.assert_cmd('{"_url": "http://test"}')
        self.assert_cmd('{"_url": none}', expected_valid=False)


    def test_op(self):
        for op in [ "put", "post" ]:
            self.assert_cmd('{"_url": "http://test", "op": "%s"}' % (op))

        self.assert_cmd('{"_url": "http://test", "op": "invald"}', expected_valid=False)


    def test_bind(self):
        self.assert_cmd('{"_url": "http://test", "bind": "bind"}')
        self.assert_cmd('{"_url": "http://test", "bind": 1234}', expected_valid=False)


    def test_retry_policy(self):
        self.assert_cmd('{"_url": "http://url", "retry-policy": []', expected_valid=False)
        self.assert_cmd('{"_url": "http://url", "retry-policy": [{"attempts": 3, "wait": "PT1M" }] }}',
                        expected_valid=False)


    def test_additional(self):
        self.assert_cmd('{"_url": "http://test", "invalid-property": 123}', expected_valid=False)



if __name__ == '__main__':
    unittest.main()
