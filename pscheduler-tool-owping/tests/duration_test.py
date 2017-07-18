"""
tests for the can-run command
"""

import pscheduler

class DurationTest(pscheduler.ToolDurationUnitTest):
    name = 'owping'

    def test_durations(self):
        self.assert_duration('{}', "PT21S")
        self.assert_duration('{"packet-interval": 0.1, "packet-count": 600}', "PT71S")
        self.assert_duration('{"packet-interval": 0.1, "packet-count": 600, "packet-timeout": 1}', "PT72S")
        
      
if __name__ == '__main__':
    unittest.main()


