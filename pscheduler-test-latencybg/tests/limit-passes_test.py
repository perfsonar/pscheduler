"""
tests for the limit-passes command
"""

import pscheduler
import unittest

class LatencyBGLimitPassesTest(pscheduler.TestLimitPassesUnitTest):
    name = 'latencybg'
        
    """
    Limit passes tests.
    """
    
    def test_endpoints(self):
       self.assert_endpoint_limits()

    def test_packet_count(self):
        self.assert_numeric_limit('packet-count', 'Packet Count', 10, 600)

    def test_packet_interval(self):
        self.assert_numeric_limit('packet-interval', 'Packet Interval', 0.001, 1)
    
    def test_duration(self):
        self.assert_duration_limit('duration', 'Duration', 'PT1M', 'PT24H')
        
    def test_report_interval(self):
        #test report-interval
        ##in range
        self.assert_cmd('{"limit": {"report-interval": {"range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "packet-count": 600, "schema": 1}}')
        ##out of range
        expected_errors = ["Report Interval not in PT30S..PT60S"]
        self.assert_cmd('{"limit": {"report-interval": {"range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "packet-count": 200, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{"limit": {"report-interval": {"range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "packet-count": 1200, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##not specified - fails if report-interval limit exists
        self.assert_cmd('{"limit": {"report-interval": {"range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "schema": 1}}', expected_valid=False)
        self.assert_cmd('{"limit": {"report-interval": {"range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-count": 600, "schema": 1}}', expected_valid=False)
        self.assert_cmd('{"limit": {"report-interval": {"range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "schema": 1}}', expected_valid=False)
        ##invert
        self.assert_cmd('{"limit": {"report-interval": {"invert": true, "range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "packet-count": 600, "schema": 1}}', expected_valid=False)
        self.assert_cmd('{"limit": {"report-interval": {"invert": true, "range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "packet-count": 200, "schema": 1}}')
        self.assert_cmd('{"limit": {"report-interval": {"invert": true, "range": {"upper": "PT60S", "lower": "PT30S"}}}, "spec": {"dest": "psched-dev1", "packet-interval": 0.1, "packet-count": 1200, "schema": 1}}')

    def test_packet_timeout(self): 
        self.assert_numeric_limit('packet-timeout', 'Packet Timeout', 1, 3)
       
    def test_packet_padding(self): 
        self.assert_numeric_limit('packet-padding', 'Packet Padding', 0, 1000)
       
    def test_ctrl_port(self): 
        self.assert_numeric_limit('ctrl-port', 'Control Ports', 861, 861)
        
    def test_data_ports(self): 
        self.assert_numeric_range_limit('data-ports', 'Data port', 8760, 9960)

    def test_ip_tos(self): 
        self.assert_numeric_list_limit('ip-tos', 'IP TOS')

    def test_ip_version(self): 
        self.assert_ip_version_limit()
    
    def test_bucket_width(self): 
        self.assert_numeric_limit('bucket-width', 'Bucket Width', 0.001, 1)
    
    def test_output_raw(self): 
        self.assert_boolean_limit('output-raw', 'Output Raw')

    def test_flip(self): 
        self.assert_boolean_limit('flip', 'Flip')
        
if __name__ == '__main__':
    unittest.main()


