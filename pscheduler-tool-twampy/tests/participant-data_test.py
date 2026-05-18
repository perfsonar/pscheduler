"""
tests for the participant-data command
"""

import pscheduler
import unittest

class ParticipantDataTest(pscheduler.ToolParticipantDataUnitTest):
    name = 'twampy'

    def test_participant_data(self):
        # STAMP is single-participant, returns empty object
        self.assert_participant_data(0, {})


if __name__ == '__main__':
    unittest.main()
