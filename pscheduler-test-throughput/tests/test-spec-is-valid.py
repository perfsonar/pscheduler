#!/usr/bin/python

import unittest
import pscheduler
import json
import os


class TestSpecIsValid(unittest.TestCase):

    path = os.path.dirname(os.path.realpath(__file__))

    def get_output(self, args, check_success=True):

        args = json.dumps(args)

        # actually run cli-to-spec with the input
        code, stdout, stderr = pscheduler.run_program("%s/../spec-is-valid" % self.path,
                                                      stdin = args)


        if check_success:
            # make sure it succeeded
            self.assertEqual(code, 0)

        # get json out
        if code != 0:
            return stderr
        return json.loads(stdout)
        

    def test_basic(self):

        # minimal
        test_input = {
            "dest": "127.0.1.1"
            }

        data = self.get_output(test_input)
        self.assertTrue(data["valid"])


        # all items
        test_input = {
            "dest": "fe80::a00:27ff:fea3:14ba",
            "dest-node": "perf.test.net",
            "source": "127.0.0.1",
            "source-node": "127.0.0.1",
            "schema": 1,
            "duration": "PT10S",
            "interval": "PT1S",
            "parallel": 1,
            "udp": True,
            "bandwidth": 1000,
            "window-size": 1000,
            "mss": 9000,
            "buffer-length": 100,
            "ip-tos": 10,
            "ip-version": 4,
            "local-address": "127.0.0.1",
            "omit": "PT10S",
            "no-delay": False,
            "congestion": "reno",
            "zero-copy": True,
            "flow-label": 1,
            "client-cpu-affinity": 1,
            "server-cpu-affinity": 1,
            "reverse": True
            }

        data = self.get_output(test_input)
        self.assertTrue(data["valid"])


    def test_bad_input(self):
        return
        # blank
        test_input = {}

        data = self.get_output(test_input)
        self.assertFalse(data["valid"])

        # bad IP address
        test_input = {"dest": "http://not.supposed.to.be.a.url"}
        data = self.get_output(test_input)
        self.assertFalse(data["valid"])

        # unknown elements
        test_input = {"not_an_option": "kittycat"}
        data = self.get_output(test_input)
        self.assertFalse(data["valid"])

        # wrong type, bandwidth is integer
        test_input = {"bandwidth": "100", "dest": "127.0.0.1"}
        data = self.get_output(test_input)
        self.assertFalse(data["valid"])
        


if __name__ == "__main__":
    unittest.main()
