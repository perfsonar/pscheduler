"""
tests for the limit-is-valid command
"""

import pscheduler

class LimitIsValidTest(pscheduler.TestLimitIsValidUnitTest):
    name = 'latencybg'
        
    """
    Limit passes tests.
    """
    
    def test_empty(self):
        #test empty
        self.assert_cmd('{}')
    
    def test_source(self):
        #test source
        ##in range
        self.assert_cmd('{"source": {"cidr": ["198.129.254.38/32"]}}')
        self.assert_cmd('{"source": {"cidr": ["2001:400:501:1150::3/128"]}}')
        ##out of range
        self.assert_cmd('{"source": {"cidr": ["198.129.254.38/33"]}}', expected_valid=False)
        self.assert_cmd('{"source": {"cidr": ["2001:400:501:1150::3/129"]}}', expected_valid=False)
        self.assert_cmd('{"source": {"cidr": ["198.129.254.38"]}}', expected_valid=False)
        self.assert_cmd('{"source": {"cidr": ["2001:400:501:1150::3"]}}', expected_valid=False)
        
    def test_dest(self):
        #test dest
        ##in range
        self.assert_cmd('{"dest": {"cidr": ["198.129.254.38/32"]}}')
        self.assert_cmd('{"dest": {"cidr": ["2001:400:501:1150::3/128"]}}')
        ##out of range
        self.assert_cmd('{"dest": {"cidr": ["198.129.254.38/33"]}}', expected_valid=False)
        self.assert_cmd('{"dest": {"cidr": ["2001:400:501:1150::3/129"]}}', expected_valid=False)
        self.assert_cmd('{"dest": {"cidr": ["198.129.254.38"]}}', expected_valid=False)
        self.assert_cmd('{"dest": {"cidr": ["2001:400:501:1150::3"]}}', expected_valid=False)
    
    def test_endpoint(self):
        #test endpoint
        ##in range
        self.assert_cmd('{"endpoint": {"cidr": ["198.129.254.38/32"]}}')
        self.assert_cmd('{"endpoint": {"cidr": ["2001:400:501:1150::3/128"]}}')
        ##out of range
        self.assert_cmd('{"endpoint": {"cidr": ["198.129.254.38/33"]}}', expected_valid=False)
        self.assert_cmd('{"endpoint": {"cidr": ["2001:400:501:1150::3/129"]}}', expected_valid=False)
        self.assert_cmd('{"endpoint": {"cidr": ["198.129.254.38"]}}', expected_valid=False)
        self.assert_cmd('{"endpoint": {"cidr": ["2001:400:501:1150::3"]}}', expected_valid=False)

    def test_packet_count(self):
        #test packet count
        ##in range
        self.assert_cmd('{"packet-count": {"range": {"upper": 600, "lower": 1}}}')
        self.assert_cmd('{"packet-count": {"range": {"upper": 600, "lower": 1}, "invert":true}}')
        ##out of range
        self.assert_cmd('{"packet-count": {"range": {"upper": 5, "lower": 10}}}', expected_valid=False, expected_errors=["Packet Count must have range where upper is greater than lower"])
        self.assert_cmd('{"packet-count": {"range": {"upper": 600, "lower": 0}}}', expected_valid=False)
        self.assert_cmd('{"packet-count": {"range": {"upper": 0, "lower": 10}}}', expected_valid=False)
        self.assert_cmd('{"packet-count": {"range": {"upper": 0, "lower": -10}}}', expected_valid=False)
        self.assert_cmd('{"packet-count": {"range": {"lower": 10}}}', expected_valid=False)
        self.assert_cmd('{"packet-count": {"range": {"upper": 600}}}', expected_valid=False)
        self.assert_cmd('{"packet-count": {"range": {"upper": 600, "lower": 10, "garbage": "stuff"}}}', expected_valid=False)
        
    def test_packet_interval(self):
        #test packet interval
        ##in range
        self.assert_cmd('{"packet-interval": {"range": {"upper": 1, "lower": 0.001}}}')
        self.assert_cmd('{"packet-interval": {"range": {"upper": 1, "lower": 0.001}, "invert":true}}')
        ##out of range
        self.assert_cmd('{"packet-interval": {"range": {"upper": 0.001, "lower": 1}}}', expected_valid=False, expected_errors=["Packet Interval must have range where upper is greater than lower"])
        self.assert_cmd('{"packet-interval": {"range": {"upper": 1, "lower": 0}}}', expected_valid=False)
        self.assert_cmd('{"packet-interval": {"range": {"upper": 0 , "lower": 1}}}', expected_valid=False)
        self.assert_cmd('{"packet-interval": {"range": {"upper": 1, "lower": -10}}}', expected_valid=False)
        self.assert_cmd('{"packet-interval": {"range": {"lower": 0.001}}}', expected_valid=False)
        self.assert_cmd('{"packet-interval": {"range": {"upper": 1}}}', expected_valid=False)
        self.assert_cmd('{"packet-interval": {"range": {"upper": 1, "lower": 0.001, "garbage": "stuff"}}}', expected_valid=False)

    def test_duration(self):
        #test duration
        ##in range
        self.assert_cmd('{"duration": {"range": {"upper": "PT60S", "lower": "PT10S"}}}')
        self.assert_cmd('{"duration": {"range": {"upper": "PT60S", "lower": "PT10S"}, "invert":true}}')
        ##out of range
        self.assert_cmd('{"duration": {"range": {"upper": "PT10S", "lower": "PT60S"}}}', expected_valid=False, expected_errors=["Duration must have range where upper is greater than lower"])
        self.assert_cmd('{"duration": {"range": {"lower": "PT10S"}}}', expected_valid=False)
        self.assert_cmd('{"duration": {"range": {"upper": "PT60S"}}}', expected_valid=False)
        self.assert_cmd('{"duration": {"range": {"upper": "PT60S", "lower": "PT10S", "garbage": "stuff"}}}', expected_valid=False)
    
    def test_report_interval(self):
        #test report-interval
        ##in range
        self.assert_cmd('{"report-interval": {"range": {"upper": "PT60S", "lower": "PT10S"}}}')
        self.assert_cmd('{"report-interval": {"range": {"upper": "PT60S", "lower": "PT10S"}, "invert":true}}')
        ##out of range
        self.assert_cmd('{"report-interval": {"range": {"upper": "PT10S", "lower": "PT60S"}}}', expected_valid=False, expected_errors=["Report Interval must have range where upper is greater than lower"])
        self.assert_cmd('{"report-interval": {"range": {"lower": "PT10S"}}}', expected_valid=False)
        self.assert_cmd('{"report-interval": {"range": {"upper": "PT60S"}}}', expected_valid=False)
        self.assert_cmd('{"report-interval": {"range": {"upper": "PT60S", "lower": "PT10S", "garbage": "stuff"}}}', expected_valid=False)
        
    def test_packet_timeout(self):
        #test packet timeout
        ##in range
        self.assert_cmd('{"packet-timeout": {"range": {"upper": 2, "lower": 0}}}')
        self.assert_cmd('{"packet-timeout": {"range": {"upper": 2, "lower": 0}, "invert":true}}')
        ##out of range
        self.assert_cmd('{"packet-timeout": {"range": {"upper": 0, "lower": 2}}}', expected_valid=False, expected_errors=["Packet Timeout must have range where upper is greater than lower"])
        self.assert_cmd('{"packet-timeout": {"range": {"upper": 0, "lower": -1}}}', expected_valid=False)
        self.assert_cmd('{"packet-timeout": {"range": {"lower": 0}}}', expected_valid=False)
        self.assert_cmd('{"packet-timeout": {"range": {"upper": 2}}}', expected_valid=False)
        self.assert_cmd('{"packet-timeout": {"range": {"upper": 2, "lower": 0, "garbage": "stuff"}}}', expected_valid=False)

    def test_packet_padding(self):
        #test packet padding
        ##in range
        self.assert_cmd('{"packet-padding": {"range": {"upper": 1000, "lower": 0}}}')
        self.assert_cmd('{"packet-padding": {"range": {"upper": 1000, "lower": 0}, "invert":true}}')
        ##out of range
        self.assert_cmd('{"packet-padding": {"range": {"upper": 0, "lower": 1000}}}', expected_valid=False, expected_errors=["Packet Padding must have range where upper is greater than lower"])
        self.assert_cmd('{"packet-padding": {"range": {"upper": 0, "lower": -1}}}', expected_valid=False)
        self.assert_cmd('{"packet-padding": {"range": {"lower": 0}}}', expected_valid=False)
        self.assert_cmd('{"packet-padding": {"range": {"upper": 1000}}}', expected_valid=False)
        self.assert_cmd('{"packet-padding": {"range": {"upper": 1000, "lower": 0, "garbage": "stuff"}}}', expected_valid=False)
    
    def test_ctrl_port(self):
        #test ctrl port
        ##in range
        self.assert_cmd('{"ctrl-port": {"range": {"upper": 861, "lower": 0}}}')
        self.assert_cmd('{"ctrl-port": {"range": {"upper": 861, "lower": 0}, "invert":true}}')
        ##out of range
        self.assert_cmd('{"ctrl-port": {"range": {"upper": 0, "lower": 861}}}', expected_valid=False, expected_errors=["Control Ports must have range where upper is greater than lower"])
        self.assert_cmd('{"ctrl-port": {"range": {"upper": 0, "lower": -1}}}', expected_valid=False)
        self.assert_cmd('{"ctrl-port": {"range": {"lower": 0}}}', expected_valid=False)
        self.assert_cmd('{"ctrl-port": {"range": {"upper": 861}}}', expected_valid=False)
        self.assert_cmd('{"ctrl-port": {"range": {"upper": 861, "lower": 0, "garbage": "stuff"}}}', expected_valid=False)
    
    def test_data_ports(self):
        #test data ports
        ##in range
        self.assert_cmd('{"data-ports": {"range": {"upper": 9960, "lower": 8760}}}')
        self.assert_cmd('{"data-ports": {"range": {"upper": 9960, "lower": 8760}, "invert":true}}')
        ##out of range
        self.assert_cmd('{"data-ports": {"range": {"upper": 8760, "lower": 9960}}}', expected_valid=False, expected_errors=["Data Ports must have range where upper is greater than lower"])
        self.assert_cmd('{"data-ports": {"range": {"upper": 8760, "lower": -1}}}', expected_valid=False)
        self.assert_cmd('{"data-ports": {"range": {"lower": 8760}}}', expected_valid=False)
        self.assert_cmd('{"data-ports": {"range": {"upper": 9960}}}', expected_valid=False)
        self.assert_cmd('{"data-ports": {"range": {"upper": 9960, "lower": 8760, "garbage": "stuff"}}}', expected_valid=False)
    
    def test_ip_tos(self):
        #test ip tos
        ##in range
        self.assert_cmd('{"ip-tos": {"match": [1, 2, 3]}}')
        self.assert_cmd('{"ip-tos": {"match": [1, 2, 3], "invert":true}}')
        ##out of range
        self.assert_cmd('{"ip-tos": {"range": {"lower": 0, "upper": 255}}}', expected_valid=False)
    
    def test_bucket_width(self):
        #test bucket-width
        ##in range
        self.assert_cmd('{"bucket-width": {"range": {"upper": 0.1, "lower": 0.001}}}')
        self.assert_cmd('{"bucket-width": {"range": {"upper": 0.1, "lower": 0.001}, "invert":true}}')
        ##out of range
        self.assert_cmd('{"bucket-width": {"range": {"upper": 0.001, "lower": 0.1}}}', expected_valid=False, expected_errors=["Bucket Width must have range where upper is greater than lower"])
        self.assert_cmd('{"bucket-width": {"range": {"upper": 1, "lower": 0}}}', expected_valid=False)
        self.assert_cmd('{"bucket-width": {"range": {"upper": 0 , "lower": 1}}}', expected_valid=False)
        self.assert_cmd('{"bucket-width": {"range": {"upper": 0.1, "lower": -10}}}', expected_valid=False)
        self.assert_cmd('{"bucket-width": {"range": {"lower": 0.001}}}', expected_valid=False)
        self.assert_cmd('{"bucket-width": {"range": {"upper": 0.1}}}', expected_valid=False)
        self.assert_cmd('{"bucket-width": {"range": {"upper": 0.1, "lower": 0.001, "garbage": "stuff"}}}', expected_valid=False)
    
    def test_ip_version(self):
        #test ip-version
        ##in range
        self.assert_cmd('{"ip-version": {"enumeration": [4,6]}}')
        self.assert_cmd('{"ip-version": {"enumeration": [6]}}')
        self.assert_cmd('{"ip-version": {"enumeration": [4]}}')
        self.assert_cmd('{"ip-version": {"enumeration": [4], "invert":true}}')
        ##out of range
        self.assert_cmd('{"ip-version": {"enumeration": [6, 7]}}', expected_valid=False)
        self.assert_cmd('{"ip-version": {"enumeration": [ 0 ]}}', expected_valid=False)
    
    def test_output_raw(self):
        #test output-raw
        ##in range
        self.assert_cmd('{"output-raw": {"match": true}}')
        self.assert_cmd('{"output-raw": {"match": false}}')
        ##out of range
        self.assert_cmd('{"output-raw": {"match": 1}}', expected_valid=False)
        self.assert_cmd('{"output-raw": {"match": 0}}', expected_valid=False)
    
    def test_flip(self):
        #test flip
        ##in range
        self.assert_cmd('{"flip": {"match": true}}')
        self.assert_cmd('{"flip": {"match": false}}')
        ##out of range
        self.assert_cmd('{"flip": {"match": 1}}', expected_valid=False)
        
if __name__ == '__main__':
    unittest.main()


