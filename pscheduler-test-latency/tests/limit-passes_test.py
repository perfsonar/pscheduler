"""
tests for the limit-passes command
"""

import unittest

import json
import os
from pscheduler import run_program
import traceback

class LimitPassesTest(unittest.TestCase):
    name = 'latency'
    vaildate_cmd = ""
    
    """
    Init with limit-passes command location
    """
    def _init_cmd(self):
        # only do this once
        if self.vaildate_cmd:
            return
        
        #find limit-passes command
        vaildate_cmd = "../{0}/limit-passes".format(self.name)
        if __file__:
            vaildate_cmd = os.path.dirname(os.path.realpath(__file__)) + '/' + vaildate_cmd
        self.vaildate_cmd =vaildate_cmd
    
    """
    Run limit-passes and verify results
    """
    def _run_cmd(self, input, expected_status=0, expected_valid=True, expected_errors=[], match_all_errors=True):
        #Run command
        self._init_cmd()
        try:
            status, stdout, stderr = run_program([self.vaildate_cmd], stdin=input)
        except:
            #print stacktrace for any errors
            traceback.print_exc()
            self.fail("unable to run limit-passes command {0}".format(self.vaildate_cmd))
        
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
            self.fail("Invalid JSON returned by limit-passes: {0}".format(stdout))
        #check fields
        assert('passes' in result_json) 
        self.assertEqual(result_json['passes'], expected_valid)
        if expected_valid:
            assert('errors' not in result_json) 
        else:
            assert('errors' in result_json) 
            if len(expected_errors) > 0 and match_all_errors:
                #verify list of errors same length
                self.assertEqual(len(result_json['errors']), len(expected_errors))
            for expected_error in expected_errors:
                #verify messages are in list
                assert(expected_error in result_json['errors'])
            
        
    """
    Limit passes tests.
    """
    
    def test_limit_passes(self):
        #test packet count
        ##in range
        self._run_cmd('{"limit": {"packet-count": {"range": {"upper": 600, "lower": 10}}}, "spec": {"dest": "psched-dev1", "packet-count": 600, "schema": 1}}')
        ##out of range
        expected_errors = ["Packet Count not in 10..600"]
        self._run_cmd('{"limit": {"packet-count": {"range": {"upper": 600, "lower": 10}}}, "spec": {"dest": "psched-dev1", "packet-count": 601, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self._run_cmd('{"limit": {"packet-count": {"range": {"upper": 600, "lower": 10}}}, "spec": {"dest": "psched-dev1", "packet-count": 5, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##not specified
        self._run_cmd('{"limit": {"packet-count": {"range": {"upper": 600, "lower": 10}}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        ##invert
        self._run_cmd('{"limit": {"packet-count": {"invert": true,"range": {"upper": 600, "lower": 10}}}, "spec": {"dest": "psched-dev1", "packet-count": 600, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"packet-count": {"invert": true,"range": {"upper": 600, "lower": 10}}}, "spec": {"dest": "psched-dev1", "packet-count": 601, "schema": 1}}')
        self._run_cmd('{"limit": {"packet-count": {"invert": true,"range": {"upper": 600, "lower": 10}}}, "spec": {"dest": "psched-dev1", "packet-count": 5, "schema": 1}}')
        
        #test packet interval
        ##in range
        self._run_cmd('{"limit": {"packet-interval": {"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "schema": 1}}')
        ##out of range
        expected_errors = ["Packet Interval not in 0.001..1"]
        self._run_cmd('{"limit": {"packet-interval": {"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.0001, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self._run_cmd('{"limit": {"packet-interval": {"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "packet-interval": 2, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##not specified
        self._run_cmd('{"limit": {"packet-interval": {"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        ##invert
        self._run_cmd('{"limit": {"packet-interval": {"invert": true,"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"packet-interval": {"invert": true,"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.0001, "schema": 1}}')
        self._run_cmd('{"limit": {"packet-interval": {"invert": true,"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "packet-interval": 2, "schema": 1}}')

        #test duration
        ##in range
        self._run_cmd('{"limit": {"duration": {"range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "packet-count": 600, "schema": 1}}')
        ##out of range
        expected_errors = ["Duration not in PT30S..PT60S"]
        self._run_cmd('{"limit": {"duration": {"range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "packet-count": 200, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self._run_cmd('{"limit": {"duration": {"range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "packet-count": 1200, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##not specified - fails if duration limit exists
        self._run_cmd('{"limit": {"duration": {"range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"duration": {"range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-count": 600, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"duration": {"range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "schema": 1}}', expected_valid=False)
        ##invert
        self._run_cmd('{"limit": {"duration": {"invert": true, "range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "packet-count": 600, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"duration": {"invert": true, "range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "packet-count": 200, "schema": 1}}')
        self._run_cmd('{"limit": {"duration": {"invert": true, "range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "packet-count": 1200, "schema": 1}}')
        
        #test packet timeout
        ##in range
        self._run_cmd('{"limit": {"packet-timeout": {"range": {"upper": 3, "lower": 1}}}, "spec": {"dest": "psched-dev1", "packet-timeout": 2, "schema": 1}}')
        ##out of range
        expected_errors = ["Packet Timeout not in 1..3"]
        self._run_cmd('{"limit": {"packet-timeout": {"range": {"upper": 3, "lower": 1}}}, "spec": {"dest": "psched-dev1", "packet-timeout": 0, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self._run_cmd('{"limit": {"packet-timeout": {"range": {"upper": 3, "lower": 1}}}, "spec": {"dest": "psched-dev1", "packet-timeout": 4, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##not specified
        self._run_cmd('{"limit": {"packet-timeout": {"range": {"upper": 3, "lower": 1}}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        ##invert
        self._run_cmd('{"limit": {"packet-timeout": {"invert": true,"range": {"upper": 3, "lower": 1}}}, "spec": {"dest": "psched-dev1", "packet-timeout": 2, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"packet-timeout": {"invert": true,"range": {"upper": 3, "lower": 1}}}, "spec": {"dest": "psched-dev1", "packet-timeout": 0, "schema": 1}}')
        self._run_cmd('{"limit": {"packet-timeout": {"invert": true,"range": {"upper": 3, "lower": 1}}}, "spec": {"dest": "psched-dev1", "packet-timeout": 4, "schema": 1}}')
        
        #test packet padding
        ##in range
        self._run_cmd('{"limit": {"packet-padding": {"range": {"upper": 1000, "lower": 0}}}, "spec": {"dest": "psched-dev1", "packet-padding": 1000, "schema": 1}}')
        ##out of range
        expected_errors = ["Packet Padding not in 0..1000"]
        self._run_cmd('{"limit": {"packet-padding": {"range": {"upper": 1000, "lower": 0}}}, "spec": {"dest": "psched-dev1", "packet-padding": 1001, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##not specified
        self._run_cmd('{"limit": {"packet-padding": {"range": {"upper": 1000, "lower": 0}}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        ##invert
        self._run_cmd('{"limit": {"packet-padding": {"invert": true,"range": {"upper": 1000, "lower": 0}}}, "spec": {"dest": "psched-dev1", "packet-padding": 1000, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"packet-padding": {"invert": true,"range": {"upper": 1000, "lower": 0}}}, "spec": {"dest": "psched-dev1", "packet-padding": 1001, "schema": 1}}')
        
        #test ctrl port - test range of 1 since don't test elsewhere and not unlikely here
        ##in range
        self._run_cmd('{"limit": {"ctrl-port": {"range": {"upper": 861, "lower": 861}}}, "spec": {"dest": "psched-dev1", "ctrl-port": 861, "schema": 1}}')
        ##out of range
        expected_errors = ["Control Ports not in 861..861"]
        self._run_cmd('{"limit": {"ctrl-port": {"range": {"upper": 861, "lower": 861}}}, "spec": {"dest": "psched-dev1", "ctrl-port": 1001, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self._run_cmd('{"limit": {"ctrl-port": {"range": {"upper": 861, "lower": 861}}}, "spec": {"dest": "psched-dev1", "ctrl-port": 860, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##not specified
        self._run_cmd('{"limit": {"ctrl-port": {"range": {"upper": 861, "lower": 861}}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        ##invert
        self._run_cmd('{"limit": {"ctrl-port": {"invert": true,"range": {"upper": 861, "lower": 0}}}, "spec": {"dest": "psched-dev1", "ctrl-port": 861, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"ctrl-port": {"invert": true,"range": {"upper": 861, "lower": 0}}}, "spec": {"dest": "psched-dev1", "ctrl-port": 1001, "schema": 1}}')
         
        #test data ports
        ##in range
        self._run_cmd('{"limit": {"data-ports": {"range": {"upper": 9960, "lower": 8760}}}, "spec": {"dest": "psched-dev1", "data-ports": {"upper": 9001, "lower": 9000}, "schema": 1}}')
        ##out of range
        expected_error_lower = ["Data port (lower bound) not in 8760..9960"]
        expected_error_upper = ["Data port (upper bound) not in 8760..9960"]
        self._run_cmd('{"limit": {"data-ports": {"range": {"upper": 9960, "lower": 8760}}}, "spec": {"dest": "psched-dev1", "data-ports": {"upper": 8760, "lower": 8759}, "schema": 1}}', expected_valid=False, expected_errors=expected_error_lower)
        self._run_cmd('{"limit": {"data-ports": {"range": {"upper": 9960, "lower": 8760}}}, "spec": {"dest": "psched-dev1", "data-ports": {"upper": 9961, "lower": 9960}, "schema": 1}}', expected_valid=False, expected_errors=expected_error_upper)
        self._run_cmd('{"limit": {"data-ports": {"range": {"upper": 9960, "lower": 8760}}}, "spec": {"dest": "psched-dev1", "data-ports": {"upper": 9971, "lower": 9970}, "schema": 1}}', expected_valid=False, expected_errors=expected_error_upper+expected_error_lower)
        self._run_cmd('{"limit": {"data-ports": {"range": {"upper": 9960, "lower": 8760}}}, "spec": {"dest": "psched-dev1", "data-ports": {"upper": 8759, "lower": 8758}, "schema": 1}}', expected_valid=False, expected_errors=expected_error_upper+expected_error_lower)
        ##not specified
        self._run_cmd('{"limit": {"data-ports": {"range": {"upper": 9960, "lower": 8760}}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        ##invert
        self._run_cmd('{"limit": {"data-ports": {"invert": true,"range": {"upper": 9960, "lower": 8760}}}, "spec": {"dest": "psched-dev1", "data-ports": {"upper": 9001, "lower": 9000}, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"data-ports": {"invert": true,"range": {"upper": 9960, "lower": 8760}}}, "spec": {"dest": "psched-dev1", "data-ports": {"upper": 8760, "lower": 8759}, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"data-ports": {"invert": true,"range": {"upper": 9960, "lower": 8760}}}, "spec": {"dest": "psched-dev1", "data-ports": {"upper": 9961, "lower": 9960}, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"data-ports": {"invert": true,"range": {"upper": 9960, "lower": 8760}}}, "spec": {"dest": "psched-dev1", "data-ports": {"upper": 9971, "lower": 9970}, "schema": 1}}')
        self._run_cmd('{"limit": {"data-ports": {"invert": true,"range": {"upper": 9960, "lower": 8760}}}, "spec": {"dest": "psched-dev1", "data-ports": {"upper": 8759, "lower": 8758}, "schema": 1}}')
        
        #test ip-tos
        ##in range
        self._run_cmd('{"limit": {"ip-tos": {"range": {"upper": 255, "lower": 0}}}, "spec": {"dest": "psched-dev1", "ip-tos": 128, "schema": 1}}')
        ##out of range
        expected_errors = ["IP TOS not in 0..255"]
        self._run_cmd('{"limit": {"ip-tos": {"range": {"upper": 255, "lower": 0}}}, "spec": {"dest": "psched-dev1", "ip-tos": 256, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##not specified
        self._run_cmd('{"limit": {"ip-tos": {"range": {"upper": 255, "lower": 0}}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        ##invert
        self._run_cmd('{"limit": {"ip-tos": {"invert": true,"range": {"upper": 255, "lower": 0}}}, "spec": {"dest": "psched-dev1", "ip-tos": 128, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"ip-tos": {"invert": true,"range": {"upper": 255, "lower": 0}}}, "spec": {"dest": "psched-dev1", "ip-tos": 256, "schema": 1}}')

        #test ip-version
        ##in range
        self._run_cmd('{"limit": {"ip-version": {"enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "ip-version": 4, "schema": 1}}')
        self._run_cmd('{"limit": {"ip-version": {"enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "ip-version": 6, "schema": 1}}')
        self._run_cmd('{"limit": {"ip-version": {"enumeration": [4]}}, "spec": {"dest": "psched-dev1", "ip-version": 4, "schema": 1}}')
        self._run_cmd('{"limit": {"ip-version": {"enumeration": [6]}}, "spec": {"dest": "psched-dev1", "ip-version": 6, "schema": 1}}')
        ##out of range
        expected_errors = ["IP Version IPv7 is not allowed"]
        self._run_cmd('{"limit": {"ip-version": {"enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "ip-version": 7, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self._run_cmd('{"limit": {"ip-version": {"enumeration": [4]}}, "spec": {"dest": "psched-dev1", "ip-version": 6, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"ip-version": {"enumeration": [6]}}, "spec": {"dest": "psched-dev1", "ip-version": 4, "schema": 1}}', expected_valid=False)
        ##not specified
        self._run_cmd('{"limit": {"ip-version": {"enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        self._run_cmd('{"limit": {"ip-version": {"enumeration": [4]}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        self._run_cmd('{"limit": {"ip-version": {"enumeration": [6]}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        ##invert
        self._run_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "ip-version": 4, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "ip-version": 6, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [4]}}, "spec": {"dest": "psched-dev1", "ip-version": 4, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [4]}}, "spec": {"dest": "psched-dev1", "ip-version": 6, "schema": 1}}')
        self._run_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "ip-version": 7, "schema": 1}}')
        self._run_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [4]}}, "spec": {"dest": "psched-dev1", "ip-version": 6, "schema": 1}}')
        self._run_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [6]}}, "spec": {"dest": "psched-dev1", "ip-version": 4, "schema": 1}}')

        #test bucket width
        ##in range
        self._run_cmd('{"limit": {"bucket-width": {"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "bucket-width": 0.1, "schema": 1}}')
        ##out of range
        expected_errors = ["Bucket Width not in 0.001..1"]
        self._run_cmd('{"limit": {"bucket-width": {"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "bucket-width": 0.0001, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self._run_cmd('{"limit": {"bucket-width": {"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "bucket-width": 2, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##not specified
        self._run_cmd('{"limit": {"bucket-width": {"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        ##invert
        self._run_cmd('{"limit": {"bucket-width": {"invert": true,"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "bucket-width": 0.1, "schema": 1}}', expected_valid=False)
        self._run_cmd('{"limit": {"bucket-width": {"invert": true,"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "bucket-width": 0.0001, "schema": 1}}')
        self._run_cmd('{"limit": {"bucket-width": {"invert": true,"range": {"upper": 1, "lower": 0.001}}}, "spec": {"dest": "psched-dev1", "bucket-width": 2, "schema": 1}}')
        
        #test output-raw
        ##in range
        self._run_cmd('{"limit": {"output-raw": {"match": true}}, "spec": {"dest": "psched-dev1", "output-raw": true, "schema": 1}}')
        self._run_cmd('{"limit": {"output-raw": {"match": false}}, "spec": {"dest": "psched-dev1", "output-raw": false, "schema": 1}}')
        self._run_cmd('{"limit": {"output-raw": {"match": false}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        ##out of range
        expected_errors = ["Output Raw testing not allowed"]
        self._run_cmd('{"limit": {"output-raw": {"match": true}}, "spec": {"dest": "psched-dev1", "output-raw": false, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self._run_cmd('{"limit": {"output-raw": {"match": false}}, "spec": {"dest": "psched-dev1", "output-raw": true, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ###not specified
        self._run_cmd('{"limit": {"output-raw": {"match": true}}, "spec": {"dest": "psched-dev1", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##with fail-message
        expected_errors = ["Test message"]
        self._run_cmd('{"limit": {"output-raw": {"match": true, "fail-message": "Test message"}}, "spec": {"dest": "psched-dev1", "output-raw": false, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self._run_cmd('{"limit": {"output-raw": {"match": false, "fail-message": "Test message"}}, "spec": {"dest": "psched-dev1", "output-raw": true, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ###not specified
        self._run_cmd('{"limit": {"output-raw": {"match": true, "fail-message": "Test message"}}, "spec": {"dest": "psched-dev1", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        
        #test flip
        ##in range
        self._run_cmd('{"limit": {"flip": {"match": true}}, "spec": {"dest": "psched-dev1", "flip": true, "schema": 1}}')
        self._run_cmd('{"limit": {"flip": {"match": false}}, "spec": {"dest": "psched-dev1", "flip": false, "schema": 1}}')
        self._run_cmd('{"limit": {"flip": {"match": false}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        ##out of range
        expected_errors = ["Flip testing not allowed"]
        self._run_cmd('{"limit": {"flip": {"match": true}}, "spec": {"dest": "psched-dev1", "flip": false, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self._run_cmd('{"limit": {"flip": {"match": false}}, "spec": {"dest": "psched-dev1", "flip": true, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ###not specified
        self._run_cmd('{"limit": {"flip": {"match": true}}, "spec": {"dest": "psched-dev1", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##with fail-message
        expected_errors = ["Test message"]
        self._run_cmd('{"limit": {"flip": {"match": true, "fail-message": "Test message"}}, "spec": {"dest": "psched-dev1", "flip": false, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self._run_cmd('{"limit": {"flip": {"match": false, "fail-message": "Test message"}}, "spec": {"dest": "psched-dev1", "flip": true, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ###not specified
        self._run_cmd('{"limit": {"flip": {"match": true, "fail-message": "Test message"}}, "spec": {"dest": "psched-dev1", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
    
        
if __name__ == '__main__':
    unittest.main()


