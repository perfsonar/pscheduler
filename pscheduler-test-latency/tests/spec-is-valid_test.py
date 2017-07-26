"""
tests for the spec-is-valid command
"""

import pscheduler
import unittest

class SpecIsValidTest(pscheduler.TestSpecIsValidUnitTest):
    name = 'latency'
    
    def test_failures(self):
        #test missing dest
        expected_errors = ["'dest' is a required property"]
        self.assert_cmd('{}', expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{"source": "10.0.0.1"}', expected_valid=False , expected_errors=expected_errors)
        
        #test garbage parameter
        expected_errors = ["Additional properties are not allowed (u'foo' was unexpected)"]
        self.assert_cmd('{"dest": "10.0.0.1", "foo": "bar"}', expected_valid=False , expected_errors=expected_errors)
    
    def test_endpoints(self):
        #test dest only
        self.assert_cmd('{"dest": "10.0.0.1"}')
        
        #test source and dest
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1"}')
        
        #test source and dest and flip
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "flip": true}')

        #test dest only with and flip
        expected_errors = ["Flipped testing requires source and dest"]
        self.assert_cmd('{"dest": "10.0.0.1", "flip": true}', expected_valid=False , expected_errors=expected_errors)
    
    def test_packet_count(self):
        ##in range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "packet-count": 600}')
        ##out of range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "packet-count": 0}', expected_valid=False)

    def test_packet_interval(self):
        ##in range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "packet-interval": 0.001}')
        ##out of range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "packet-interval": "blah"}', expected_valid=False)

    def test_packet_timeout(self):
        ##in range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "packet-timeout": 1}')
        ##out of range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "packet-timeout": "blah"}', expected_valid=False)
    
    def test_packet_padding(self):
        ##in range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "packet-padding": 0}')
        ##out of range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "packet-padding": "blah"}', expected_valid=False)
    
    def test_ctrl_port(self):
        ##in range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "ctrl-port": 861}')
        ##out of range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "ctrl-port": "blah"}', expected_valid=False)
    
    def test_data_ports(self):
        ##in range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "data-ports": {"lower": 2000, "upper": 3000}}')
        ##out of range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "data-ports": "blah"}', expected_valid=False)
    
    def test_ip_tos(self):
        ##in range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "ip-tos": 128}')
        ##out of range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "ip-tos": "blah"}', expected_valid=False)
    
    def test_bucket_width(self):
        ##in range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "bucket-width": 0.001}')
        ##out of range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "bucket-width": "blah"}', expected_valid=False)
    
    def test_ip_version(self):
        ##in range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "ip-version": 6}')
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "ip-version": 4}')
        ##out of range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "ip-version": 7}', expected_valid=False)
    
    def test_output_raw(self):
        ##in range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "output-raw": true}')
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "output-raw": false}')
        ##out of range
        self.assert_cmd('{"source": "lbl-pt1.es.net", "dest": "10.0.0.1", "output-raw": 7}', expected_valid=False)

        
if __name__ == '__main__':
    unittest.main()


