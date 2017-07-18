"""
tests for the participant-data command
"""

import pscheduler
import unittest

class ParticipantDataTest(pscheduler.ToolParticipantDataUnitTest):
    name = 'powstream'

    def test_participant_data(self):
        #doesn't really do much so simple test to make sure it runs and returns empty object
        self.assert_participant_data(0, {})
        
      
if __name__ == '__main__':
    unittest.main()


