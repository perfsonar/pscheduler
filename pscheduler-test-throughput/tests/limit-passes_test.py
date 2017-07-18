import pscheduler

import os
from json import dumps

class TestLimitPasses(pscheduler.TestLimitPassesUnitTest):
    name = 'throughput'

    def test_endpoints(self):
         self.assert_endpoint_limits()
    
    def test_bandwidth(self):
        self.assert_sinumber_limit('bandwidth', 'Bandwidth', '100M', '1G')
        self.assert_numeric_limit('bandwidth', 'Bandwidth', 100000000, 1000000000)
    
    def test_duration(self):
        self.assert_duration_limit('duration', 'Duration', 'PT15S', 'PT30S')
    
    def test_udp(self):
        self.assert_boolean_limit('udp', 'UDP')
    
    def test_ip_version(self):
        self.assert_ip_version_limit()
    
    def test_parallel(self):
        self.assert_numeric_limit('parallel', "Parallel", 1, 3)  

if __name__ == "__main__":
    unittest.main()
