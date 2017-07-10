"""
tests for the can-run command
"""

import pscheduler

class DurationTest(pscheduler.ToolDurationUnitTest):
    name = 'powstream'

    def test_durations(self):
        self.assert_duration('{}', "PT24H")
        self.assert_duration('{"packet-interval": 0.1, "packet-count": 600}', "PT24H")
        self.assert_duration('{"duration": "PT15M"}', "PT15M")
        
      
if __name__ == '__main__':
    unittest.main()


