#!/usr/bin/python

import unittest
import pscheduler
import json
import os


class TestParticipants(unittest.TestCase):

    path = os.path.dirname(os.path.realpath(__file__))

    def get_output(self, args, check_success=True):

        args = json.dumps(args)

        # actually run cli-to-spec with the input
        code, stdout, stderr = pscheduler.run_program("%s/../participants" % self.path,
                                                      stdin = args)


        if check_success:
            # make sure it succeeded
            self.assertEqual(code, 0)

        # get json out
        if code != 0:
            return stderr
        return json.loads(stdout)
        

    def test_basic(self):

        # SKIPPING THIS TEST FOR NOW BECAUSE
        # OF THE BWCTL BACKWARDS COMPAT ISSUE
        # When trying to run unit tests on a host not actively
        # running pscheduler this fails because it can't figure out
        # whether to use pscheduler or bwctl
        return

        # Junk test input, but have to ensure we're only
        # looking at localhost for tests
        test_input = {
            "source": "localhost",
            "dest": "localhost"
            }

        data = self.get_output(test_input)

        self.assertTrue(len(data['participants']) == 2)
        self.assertEqual(data["participants"][0], test_input["source"])
        self.assertEqual(data["participants"][1], test_input["dest"])

    def test_null_input(self):        
        # missing source
        test_input = {
            "dest": "127.0.0.1"
            }

        data = self.get_output(test_input)
        self.assertEqual(data["null-reason"], "No source specified")


    def test_bad_input(self):        
        # missing dest
        test_input = {
            "source": "127.0.0.1"
            }

        data = self.get_output(test_input, check_success=False)
        self.assertEqual(data, "Missing destination argument in spec\n")


if __name__ == "__main__":
    unittest.main()
