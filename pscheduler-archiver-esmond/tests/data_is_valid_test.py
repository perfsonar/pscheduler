"""
tests for the data-is-valid command
"""

import pscheduler
import unittest

class DataIsValidTest(pscheduler.ArchiverDataIsValidUnitTest):
    name = 'esmond'
        
    def _test_host(self, field_name):
        self.assert_cmd('{{"{0}": "127.0.0.1", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}}'.format(field_name))
        self.assert_cmd('{{"{0}": "fe80::a00:27ff:fe04:4faa", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}}'.format(field_name))
        self.assert_cmd('{{"{0}": "::1", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}}'.format(field_name))
        self.assert_cmd('{{"{0}": "example.perfsonar.net", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}}'.format(field_name))
        self.assert_cmd('{{"{0}": "bad address", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}}'.format(field_name), expected_valid=False)
    
    """
    Data validation tests.
    """
    
    def test_url(self):
        #test URL
        ##valid url
        self.assert_cmd('{"url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        ##invalid url
        self.assert_cmd('{"url": 1}',  expected_valid=False)
        #missing URL
        self.assert_cmd('{"url2": "https/example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        #invalid json
        self.assert_cmd('{"url: "https/example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
    
    def test_schema(self):
        #test schema version
        self.assert_cmd('{"schema": 1, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"schema": 2, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False, expected_errors=["Schema version 2 is not supported (highest is 1)"])
    
    def test_bind(self):
        #test bind
        self._test_host("bind")
    
    def test_auth_token(self):
        #test _auth_token
        self.assert_cmd('{"_auth-token": "2bc72c85c507f4c79825640ed640ce3cf24e2768", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"_auth-token": 1, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
    
    def test_measurement_agent(self): 
        #test measurement-agent
        self._test_host("measurement-agent")
    
    def test_verify_ssl(self): 
        #test verify-ssl
        self.assert_cmd('{"verify-ssl": true, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"verify-ssl": false, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"verify-ssl": 0, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"verify-ssl": 1, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"verify-ssl": maybe, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
    
    def test_data_formatting_policy(self):
        #test data-formatting-policy
        self.assert_cmd('{"data-formatting-policy": "prefer-mapped", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"data-formatting-policy": "mapped-and-raw", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"data-formatting-policy": "mapped-only", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"data-formatting-policy": "raw-only", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"data-formatting-policy": "bad-input", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
    
    def test_retry_policy(self):
        #test retry-policy
        self.assert_cmd('{"retry-policy": [], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"retry-policy": [{"attempts": 2, "wait": "PT60S"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"retry-policy": [{"attempts": 2, "wait": "PT60S"}, {"attempts": 3, "wait": "PT120S"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"retry-policy": [{"attempts": 2, "wait": "PT60S"}, {"attempts": 3, "wait": "PT120S"}, {"attempts": 1, "wait": "P1D"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"retry-policy": "", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"retry-policy": [{}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"retry-policy": [{"attempts": 2], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"retry-policy": [{"attempts": 0, "wait": "PT60S"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"retry-policy": [{"wait": "PT60S"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"retry-policy": [{"attempts": 2, "wait": 60}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"retry-policy": [{"attempts": 2, "wait": "PU60S"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
    
    def test_summaries(self):
        #test summaries
        self.assert_cmd('{"summaries": [], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"summaries": [{"event-type": "throughput", "summary-type": "average", "summary-window": 86400}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"summaries": [{"event-type": "throughput", "summary-type": "average", "summary-window": 86400}, {"event-type": "histogram-owdelay", "summary-type": "statistics", "summary-window": 0}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self.assert_cmd('{"summaries": "", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"summaries": [{}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"summaries": [{"event-type": "throughput"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"summaries": [{"summary-type": "average"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"summaries": [{"summary-window": 86400}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self.assert_cmd('{"summaries": [{"event-type": "throughput", "summary-type": "average", "summary-window": "86400"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)

if __name__ == '__main__':
    unittest.main()


