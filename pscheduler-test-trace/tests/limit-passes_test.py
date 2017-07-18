"""
tests for the limit-passes command
"""

import pscheduler


class TraceLimitPassesTest(pscheduler.TestLimitPassesUnitTest):
    name = 'trace'
        
    """
    Limit passes tests.
    """
    
    def test_endpoints(self):
       self.assert_endpoint_limits()
    
    def test_algorithm(self):
        self.assert_string_limit('algorithm', 'Algorithm')
        
    def test_as(self):
        self.assert_boolean_limit('as', 'AS resolution')
    
    def test_dest_port(self):
        self.assert_numeric_limit('dest-port', 'Destination port', 8080, 9090)
    
    def test_first_ttl(self):
        self.assert_numeric_limit('first-ttl', 'First time to live', 1, 2)
        
    def test_fragment(self):
        self.assert_boolean_limit('fragment', 'Fragmentation')
    
    def test_hops(self):
        self.assert_numeric_limit('hops', 'Number of hops', 64, 64)

    def test_hostnames(self):
        self.assert_boolean_limit('hostnames', 'Hostname resolution')

    def test_ip_tos(self): 
        self.assert_numeric_list_limit('ip-tos', 'IP TOS')

    def test_ip_version(self): 
        self.assert_ip_version_limit()
        
    def test_length(self):
        self.assert_numeric_limit('length', 'Length', 100, 1000)
        
    def test_hostnames(self):
        self.assert_boolean_limit("hostnames", "Hostname resolution")
    
    def test_probe_type(self):
        self.assert_string_limit('probe-type', 'Probe type')
        
    def test_queries(self):
        self.assert_numeric_limit('queries', 'Number of queries', 1, 3)
    
    def test_send_wait(self):
        self.assert_duration_limit('send-wait', 'Send wait', 'PT1S', 'PT10S',)
    
    def test_wait(self):
        self.assert_duration_limit('wait', 'Wait', 'PT1S', 'PT10S',)

    
            
if __name__ == '__main__':
    unittest.main()


