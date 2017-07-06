#!/usr/bin/python

import pscheduler
from json import dumps


# SKIPPING THIS TEST FOR NOW BECAUSE
# OF THE BWCTL BACKWARDS COMPAT ISSUE
# When trying to run unit tests on a host not actively
# running pscheduler this fails because it can't figure out
# whether to use pscheduler or bwctl


class TestParticipants(pscheduler.TestParticipantsUnitTest):
    name="throughput"

    def test_basic(self):
        # HACK
        return

        # Junk test input, but have to ensure we're only
        # looking at localhost for tests
        test_input = {
            "source": "localhost",
            "dest": "localhost"
            }
        expected = [test_input["source"], test_input["dest"]] 
        self.assert_participants(test_input, expected)

    def test_null_input(self):
        # HACK
        return
    
        # missing source
        test_input = {
            "dest": "127.0.0.1"
            }
        expected = [None, test_input["dest"]] 
        self.assert_participants(test_input, expected, null_reason="No source specified")


    def test_bad_input(self):
        # HACK
        return
        
        # missing dest
        test_input = {
            "source": "127.0.0.1"
            }
        self.run_cmd(
            dumps(test_input), 
            expected_status=1, 
            json_out=False,
            expected_stderr="Missing destination argument in spec\n"
        )


if __name__ == "__main__":
    unittest.main()
