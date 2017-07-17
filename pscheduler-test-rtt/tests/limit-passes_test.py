"""
tests for the limit-passes command
"""

import pscheduler


class RTTLimitPassesTest(pscheduler.TestLimitPassesUnitTest):
    name = 'rtt'
        
    """
    Limit passes tests.
    """
    
    def test_endpoints(self):
       self.assert_endpoint_limits()
  
    def test_count(self):
        self.assert_numeric_limit('count', 'Count', 1, 600)
    
    def test_flow_label(self):
        self.assert_numeric_list_limit('flow-label', 'Flow label')
    
    def test_ip_tos(self):
        self.assert_numeric_list_limit('ip-tos', 'IP TOS')
    
    def test_length(self):
        self.assert_numeric_limit('length', 'Length', 100, 1000)
    
    def test_ttl(self):
        self.assert_numeric_limit('ttl', 'Time to live', 10, 255)
    
    def test_ip_version(self):
        self.assert_ip_version_limit()
        
    def test_hostnames(self):
        self.assert_boolean_limit("hostnames", "Hostname resolution")
    
    def test_suppress_loopback(self):
        self.assert_boolean_limit("suppress-loopback", "Suppress loopback")
    
    def test_interval(self):
        self.assert_duration_limit("interval", "Interval", "PT1S", "PT5S")
    
    def test_timeout(self):
        self.assert_duration_limit("timeout", "Timeout", "PT30S", "PT2M")
    
    def test_deadline(self):
        self.assert_duration_limit("deadline", "Deadline", "PT1M", "PT3M")
        
        
if __name__ == '__main__':
    unittest.main()
