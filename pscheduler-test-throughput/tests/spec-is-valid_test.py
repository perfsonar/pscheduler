import pscheduler
from json import dumps
import unittest

class TestSpecIsValid(pscheduler.TestSpecIsValidUnitTest):
    name="throughput"        

    def test_basic(self):

        # minimal
        test_input = {
            "dest": "127.0.1.1"
            }

        self.assert_cmd(dumps(test_input))


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
            "single-ended": True,
            "single-ended-port": 5000,
            "reverse": True
            }

        self.assert_cmd(dumps(test_input))


    def test_bad_input(self):
        return
        # blank
        test_input = {}
        self.assert_cmd(dumps(test_input), expected_valid=False)

        # bad IP address
        test_input = {"dest": "http://not.supposed.to.be.a.url"}
        self.assert_cmd(dumps(test_input), expected_valid=False)

        # unknown elements
        test_input = {"not_an_option": "kittycat"}
        self.assert_cmd(dumps(test_input), expected_valid=False)

        # wrong type, bandwidth is integer
        test_input = {"bandwidth": "100", "dest": "127.0.0.1"}
        self.assert_cmd(dumps(test_input), expected_valid=False)
        


if __name__ == "__main__":
    unittest.main()
