"""
tests for the participants command
"""

import pscheduler

class ParticipantsTest(pscheduler.TestParticipantsUnitTest):
    name = 'latency'
    
    def test_participants(self):
        self.assert_participants('{"source": "10.0.0.1", "dest": "10.0.0.2"}', ["10.0.0.1"])
        self.assert_participants('{"source": "10.0.0.1", "dest": "10.0.0.2", "flip": true}', ["10.0.0.2"])
        self.assert_participants('{"dest": "10.0.0.2"}', [None], null_reason="No source specified")

        
if __name__ == '__main__':
    unittest.main()
