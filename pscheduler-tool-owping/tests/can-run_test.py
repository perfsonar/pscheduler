"""
tests for the can-run command
"""

import pscheduler

class CanRunTest(pscheduler.ToolCanRunUnitTest):
    name = 'owping'

    def test_invalid(self):
        #empty
        expected_errors=["Missing test type"]
        self.assert_cmd('{}', expected_valid=False, expected_errors=expected_errors)
        #missing type
        self.assert_cmd(
            '{"spec":{"dest": "10.0.1.1", "schema": 1}}', 
            expected_valid=False,
            expected_errors=expected_errors
        )
        #invalid type
        expected_errors=["Unsupported test type"]
        self.assert_cmd(
            '{"type":"foo", "spec":{"dest": "10.0.1.1", "schema": 1}}', 
            expected_valid=False,
            expected_errors=expected_errors
        )
        #missing spec
        expected_errors=["Missing test specification"]
        self.assert_cmd(
            '{"type":"latency"}',
            expected_valid=False, 
            expected_errors=expected_errors
        )
    
    def test_valid(self):
        self.assert_cmd('{"type":"latency", "spec":{"dest": "10.0.1.1", "schema": 1}}')
      
if __name__ == '__main__':
    unittest.main()


