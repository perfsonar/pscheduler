"""
tests for the duration command
"""

import pscheduler
import unittest

class DurationTest(pscheduler.ToolDurationUnitTest):
    name = 'twampy'

    def test_durations(self):
        # default: (0.1 * 100) + 0 + 10 + 1 = 21s
        self.assert_duration('{"spec":{}}', "PT21S")
        # custom count: (0.1 * 600) + 0 + 10 + 1 = 71s
        self.assert_duration('{"spec":{"packet-interval": 0.1, "packet-count": 600}}', "PT71S")
        # custom timeout: (0.1 * 600) + 1 + 10 + 1 = 72s
        self.assert_duration('{"spec":{"packet-interval": 0.1, "packet-count": 600, "packet-timeout": 1}}', "PT72S")


if __name__ == '__main__':
    unittest.main()
