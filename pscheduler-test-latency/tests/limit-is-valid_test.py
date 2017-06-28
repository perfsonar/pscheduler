"""
tests for the limit-is-valid command
"""

import unittest

import json
import os
from pscheduler import run_program
import traceback

class LimitIsValidTest(unittest.TestCase):
    name = 'latency'
    result_valid_field = "valid"
    error_field = "message"
    
    """
    Init with limit-is-valid command location
    """
    def __init__(self, *args, **kwargs):
        super(LimitIsValidTest, self).__init__(*args, **kwargs)
        #find limit-is-valid command
        vaildate_cmd = "../{0}/limit-is-valid".format(self.name)
        if __file__:
            vaildate_cmd = os.path.dirname(os.path.realpath(__file__)) + '/' + vaildate_cmd
        self.vaildate_cmd = vaildate_cmd
    
    """
    Run limit-is-valid and verify results
    """
    def _run_cmd(self, input, expected_status=0, expected_valid=True, expected_error=""):
        #Run command
        try:
            status, stdout, stderr = run_program([self.vaildate_cmd], stdin=input)
        except:
            #print stacktrace for any errors
            traceback.print_exc()
            self.fail("unable to run limit-is-valid command {0}".format(self.vaildate_cmd))
        
        #check stdout and stderr
        print stdout
        print stderr
        self.assertEqual(status, expected_status) #status should be 0
        self.assertFalse(stderr) #stderr should be empty
        #check for valid JSON
        try:
            result_json = json.loads(stdout)
        except:
            traceback.print_exc()
            self.fail("Invalid JSON returned by limit-is-valid: {0}".format(stdout))
        #check fields
        assert(self.result_valid_field in result_json) 
        self.assertEqual(result_json[self.result_valid_field], expected_valid)
        if expected_valid:
            assert(self.error_field not in result_json) 
        else:
            assert(self.error_field in result_json) 
            if expected_error:
                self.assertEqual(result_json[self.error_field], expected_error)
            
        
    """
    Limit passes tests.
    """
    
    def test_limit_passes(self):
        #test empty
        self._run_cmd('{}')
        
        #test packet count
        ##in range
        self._run_cmd('{"packet-count": {"range": {"upper": 600, "lower": 1}}}')
        self._run_cmd('{"packet-count": {"range": {"upper": 600, "lower": 1}, "invert":true}}')
        ##out of range
        self._run_cmd('{"packet-count": {"range": {"upper": 5, "lower": 10}}}', expected_valid=False, expected_error="Packet Count must have range where upper is greater than lower")
        self._run_cmd('{"packet-count": {"range": {"upper": 600, "lower": 0}}}', expected_valid=False)
        self._run_cmd('{"packet-count": {"range": {"upper": 0, "lower": 10}}}', expected_valid=False)
        self._run_cmd('{"packet-count": {"range": {"upper": 0, "lower": -10}}}', expected_valid=False)
        self._run_cmd('{"packet-count": {"range": {"lower": 10}}}', expected_valid=False)
        self._run_cmd('{"packet-count": {"range": {"upper": 600}}}', expected_valid=False)
        self._run_cmd('{"packet-count": {"range": {"upper": 600, "lower": 10, "garbage": "stuff"}}}', expected_valid=False)
        
        #test packet interval
        ##in range
        self._run_cmd('{"packet-interval": {"range": {"upper": 1, "lower": 0.001}}}')
        self._run_cmd('{"packet-interval": {"range": {"upper": 1, "lower": 0.001}, "invert":true}}')
        ##out of range
        self._run_cmd('{"packet-interval": {"range": {"upper": 0.001, "lower": 1}}}', expected_valid=False, expected_error="Packet Interval must have range where upper is greater than lower")
        self._run_cmd('{"packet-interval": {"range": {"upper": 1, "lower": 0}}}', expected_valid=False)
        self._run_cmd('{"packet-interval": {"range": {"upper": 0 , "lower": 1}}}', expected_valid=False)
        self._run_cmd('{"packet-interval": {"range": {"upper": 1, "lower": -10}}}', expected_valid=False)
        self._run_cmd('{"packet-interval": {"range": {"lower": 0.001}}}', expected_valid=False)
        self._run_cmd('{"packet-interval": {"range": {"upper": 1}}}', expected_valid=False)
        self._run_cmd('{"packet-interval": {"range": {"upper": 1, "lower": 0.001, "garbage": "stuff"}}}', expected_valid=False)
        
        #test duration
        ##in range
        self._run_cmd('{"duration": {"range": {"upper": "PT60S", "lower": "PT10S"}}}')
        self._run_cmd('{"duration": {"range": {"upper": "PT60S", "lower": "PT10S"}, "invert":true}}')
        ##out of range
        self._run_cmd('{"duration": {"range": {"upper": "PT10S", "lower": "PT60S"}}}', expected_valid=False, expected_error="Duration must have range where upper is greater than lower")
        self._run_cmd('{"duration": {"range": {"lower": "PT10S"}}}', expected_valid=False)
        self._run_cmd('{"duration": {"range": {"upper": "PT60S"}}}', expected_valid=False)
        self._run_cmd('{"duration": {"range": {"upper": "PT60S", "lower": "PT10S", "garbage": "stuff"}}}', expected_valid=False)
        
        #test packet timeout
        ##in range
        self._run_cmd('{"packet-timeout": {"range": {"upper": 2, "lower": 0}}}')
        self._run_cmd('{"packet-timeout": {"range": {"upper": 2, "lower": 0}, "invert":true}}')
        ##out of range
        self._run_cmd('{"packet-timeout": {"range": {"upper": 0, "lower": 2}}}', expected_valid=False, expected_error="Packet Timeout must have range where upper is greater than lower")
        self._run_cmd('{"packet-timeout": {"range": {"upper": 0, "lower": -1}}}', expected_valid=False)
        self._run_cmd('{"packet-timeout": {"range": {"lower": 0}}}', expected_valid=False)
        self._run_cmd('{"packet-timeout": {"range": {"upper": 2}}}', expected_valid=False)
        self._run_cmd('{"packet-timeout": {"range": {"upper": 2, "lower": 0, "garbage": "stuff"}}}', expected_valid=False)
        
        #test packet padding
        ##in range
        self._run_cmd('{"packet-padding": {"range": {"upper": 1000, "lower": 0}}}')
        self._run_cmd('{"packet-padding": {"range": {"upper": 1000, "lower": 0}, "invert":true}}')
        ##out of range
        self._run_cmd('{"packet-padding": {"range": {"upper": 0, "lower": 1000}}}', expected_valid=False, expected_error="Packet Padding must have range where upper is greater than lower")
        self._run_cmd('{"packet-padding": {"range": {"upper": 0, "lower": -1}}}', expected_valid=False)
        self._run_cmd('{"packet-padding": {"range": {"lower": 0}}}', expected_valid=False)
        self._run_cmd('{"packet-padding": {"range": {"upper": 1000}}}', expected_valid=False)
        self._run_cmd('{"packet-padding": {"range": {"upper": 1000, "lower": 0, "garbage": "stuff"}}}', expected_valid=False)
        
        #test ctrl port
        ##in range
        self._run_cmd('{"ctrl-port": {"range": {"upper": 861, "lower": 0}}}')
        self._run_cmd('{"ctrl-port": {"range": {"upper": 861, "lower": 0}, "invert":true}}')
        ##out of range
        self._run_cmd('{"ctrl-port": {"range": {"upper": 0, "lower": 861}}}', expected_valid=False, expected_error="Control Ports must have range where upper is greater than lower")
        self._run_cmd('{"ctrl-port": {"range": {"upper": 0, "lower": -1}}}', expected_valid=False)
        self._run_cmd('{"ctrl-port": {"range": {"lower": 0}}}', expected_valid=False)
        self._run_cmd('{"ctrl-port": {"range": {"upper": 861}}}', expected_valid=False)
        self._run_cmd('{"ctrl-port": {"range": {"upper": 861, "lower": 0, "garbage": "stuff"}}}', expected_valid=False)
        
        #test data ports
        ##in range
        self._run_cmd('{"data-ports": {"range": {"upper": 9960, "lower": 8760}}}')
        self._run_cmd('{"data-ports": {"range": {"upper": 9960, "lower": 8760}, "invert":true}}')
        ##out of range
        self._run_cmd('{"data-ports": {"range": {"upper": 8760, "lower": 9960}}}', expected_valid=False, expected_error="Data Ports must have range where upper is greater than lower")
        self._run_cmd('{"data-ports": {"range": {"upper": 8760, "lower": -1}}}', expected_valid=False)
        self._run_cmd('{"data-ports": {"range": {"lower": 8760}}}', expected_valid=False)
        self._run_cmd('{"data-ports": {"range": {"upper": 9960}}}', expected_valid=False)
        self._run_cmd('{"data-ports": {"range": {"upper": 9960, "lower": 8760, "garbage": "stuff"}}}', expected_valid=False)
        
        #test ip tos
        ##in range
        self._run_cmd('{"ip-tos": {"range": {"upper": 255, "lower": 0}}}')
        self._run_cmd('{"ip-tos": {"range": {"upper": 255, "lower": 0}, "invert":true}}')
        ##out of range
        self._run_cmd('{"ip-tos": {"range": {"upper": 0, "lower": 255}}}', expected_valid=False, expected_error="IP TOS must have range where upper is greater than lower")
        self._run_cmd('{"ip-tos": {"range": {"upper": 0, "lower": -1}}}', expected_valid=False)
        self._run_cmd('{"ip-tos": {"range": {"lower": 0}}}', expected_valid=False)
        self._run_cmd('{"ip-tos": {"range": {"upper": 255}}}', expected_valid=False)
        self._run_cmd('{"ip-tos": {"range": {"upper": 255, "lower": 0, "garbage": "stuff"}}}', expected_valid=False)

        #test bucket-width
        ##in range
        self._run_cmd('{"bucket-width": {"range": {"upper": 0.1, "lower": 0.001}}}')
        self._run_cmd('{"bucket-width": {"range": {"upper": 0.1, "lower": 0.001}, "invert":true}}')
        ##out of range
        self._run_cmd('{"bucket-width": {"range": {"upper": 0.001, "lower": 0.1}}}', expected_valid=False, expected_error="Bucket Width must have range where upper is greater than lower")
        self._run_cmd('{"bucket-width": {"range": {"upper": 1, "lower": 0}}}', expected_valid=False)
        self._run_cmd('{"bucket-width": {"range": {"upper": 0 , "lower": 1}}}', expected_valid=False)
        self._run_cmd('{"bucket-width": {"range": {"upper": 0.1, "lower": -10}}}', expected_valid=False)
        self._run_cmd('{"bucket-width": {"range": {"lower": 0.001}}}', expected_valid=False)
        self._run_cmd('{"bucket-width": {"range": {"upper": 0.1}}}', expected_valid=False)
        self._run_cmd('{"bucket-width": {"range": {"upper": 0.1, "lower": 0.001, "garbage": "stuff"}}}', expected_valid=False)
        
        #test ip-version
        ##in range
        self._run_cmd('{"ip-version": {"enumeration": [4,6]}}')
        self._run_cmd('{"ip-version": {"enumeration": [6]}}')
        self._run_cmd('{"ip-version": {"enumeration": [4]}}')
        self._run_cmd('{"ip-version": {"enumeration": [4], "invert":true}}')
        ##out of range
        self._run_cmd('{"ip-version": {"enumeration": [6, 7]}}', expected_valid=False)
        self._run_cmd('{"ip-version": {"enumeration": [ 0 ]}}', expected_valid=False)
        
        #test output-raw
        ##in range
        self._run_cmd('{"output-raw": {"match": true}}')
        self._run_cmd('{"output-raw": {"match": false}}')
        ##out of range
        self._run_cmd('{"output-raw": {"match": 1}}', expected_valid=False)
        self._run_cmd('{"output-raw": {"match": 0}}', expected_valid=False)
        
        #test flip
        ##in range
        self._run_cmd('{"flip": {"match": true}}')
        self._run_cmd('{"flip": {"match": false}}')
        ##out of range
        self._run_cmd('{"flip": {"match": 1}}', expected_valid=False)
        
if __name__ == '__main__':
    unittest.main()


