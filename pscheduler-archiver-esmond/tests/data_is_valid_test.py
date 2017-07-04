"""
tests for the data-is-valid command
"""

import unittest

import json
import os
from pscheduler import run_program
import traceback

class DataIsValidTest(unittest.TestCase):
    name = 'esmond'
    vaildate_cmd = ""
    
    """
    Init with data-is-valid command location
    """
    def _init_cmd(self):
        # only do this once
        if self.vaildate_cmd:
            return
        
        #find data-is-valid command
        vaildate_cmd = "../{0}/data-is-valid".format(self.name)
        if __file__:
            vaildate_cmd = os.path.dirname(os.path.realpath(__file__)) + '/' + vaildate_cmd
        self.vaildate_cmd =vaildate_cmd
    
    """
    Run data-is-valid and verify results
    """
    def _run_cmd(self, input, expected_status=0, expected_valid=True, expected_error=""):
        #Run command
        self._init_cmd()
        try:
            status, stdout, stderr = run_program([self.vaildate_cmd], stdin=input)
        except:
            #print stacktrace for any errors
            traceback.print_exc()
            self.fail("unable to run data-is-valid command {0}".format(self.vaildate_cmd))
        
        #check stdout and stderr
        self.assertEqual(status, expected_status) #status should be 0
        self.assertFalse(stderr) #stderr should be empty
        #check for valid JSON
        try:
            result_json = json.loads(stdout)
        except:
            traceback.print_exc()
            self.fail("Invalid JSON returned by data-is-valid: {0}".format(stdout))
        #check fields
        assert('valid' in result_json) 
        self.assertEqual(result_json['valid'], expected_valid)
        if expected_valid:
            assert('error' not in result_json) 
        else:
            assert('error' in result_json) 
            if expected_error:
                self.assertEqual(result_json['error'], expected_error)
    
    def _test_host(self, field_name):
        self._run_cmd('{{"{0}": "127.0.0.1", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}}'.format(field_name))
        self._run_cmd('{{"{0}": "fe80::a00:27ff:fe04:4faa", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}}'.format(field_name))
        self._run_cmd('{{"{0}": "::1", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}}'.format(field_name))
        self._run_cmd('{{"{0}": "example.perfsonar.net", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}}'.format(field_name))
        self._run_cmd('{{"{0}": "bad address", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}}'.format(field_name), expected_valid=False)
    
    """
    Data validation tests.
    """
    
    def test_data_is_valid(self):
        #test URL
        ##valid url
        self._run_cmd('{"url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        ##invalid url
        self._run_cmd('{"url": 1}',  expected_valid=False)
        #missing URL
        self._run_cmd('{"url2": "https/example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        #invalid json
        self._run_cmd('{"url: "https/example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        
        #test schema version
        self._run_cmd('{"schema": 1, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"schema": 2, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False, expected_error="Schema version 2 is not supported (highest is 1)")
        
        #test bind
        self._test_host("bind")
        
        #test _auth_token
        self._run_cmd('{"_auth-token": "2bc72c85c507f4c79825640ed640ce3cf24e2768", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"_auth-token": 1, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        
        #test measurement-agent
        self._test_host("measurement-agent")
        
        #test verify-ssl
        self._run_cmd('{"verify-ssl": true, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"verify-ssl": false, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"verify-ssl": 0, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"verify-ssl": 1, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"verify-ssl": maybe, "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        
        #test data-formatting-policy
        self._run_cmd('{"data-formatting-policy": "prefer-mapped", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"data-formatting-policy": "mapped-and-raw", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"data-formatting-policy": "mapped-only", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"data-formatting-policy": "raw-only", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"data-formatting-policy": "bad-input", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        
        #test retry-policy
        self._run_cmd('{"retry-policy": [], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"retry-policy": [{"attempts": 2, "wait": "PT60S"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"retry-policy": [{"attempts": 2, "wait": "PT60S"}, {"attempts": 3, "wait": "PT120S"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"retry-policy": [{"attempts": 2, "wait": "PT60S"}, {"attempts": 3, "wait": "PT120S"}, {"attempts": 1, "wait": "P1D"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"retry-policy": "", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"retry-policy": [{}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"retry-policy": [{"attempts": 2], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"retry-policy": [{"attempts": 0, "wait": "PT60S"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"retry-policy": [{"wait": "PT60S"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"retry-policy": [{"attempts": 2, "wait": 60}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"retry-policy": [{"attempts": 2, "wait": "PU60S"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        
        #test summaries
        self._run_cmd('{"summaries": [], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"summaries": [{"event-type": "throughput", "summary-type": "average", "summary-window": 86400}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"summaries": [{"event-type": "throughput", "summary-type": "average", "summary-window": 86400}, {"event-type": "histogram-owdelay", "summary-type": "statistics", "summary-window": 0}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}')
        self._run_cmd('{"summaries": "", "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"summaries": [{}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"summaries": [{"event-type": "throughput"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"summaries": [{"summary-type": "average"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"summaries": [{"summary-window": 86400}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)
        self._run_cmd('{"summaries": [{"event-type": "throughput", "summary-type": "average", "summary-window": "86400"}], "url": "https://example.perfsonar.net/esmond/perfsonar/archive"}', expected_valid=False)

if __name__ == '__main__':
    unittest.main()


