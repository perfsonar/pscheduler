#!/usr/bin/python

import unittest
import pscheduler
import json
import os


class TestCliToSpec(unittest.TestCase):

    path = os.path.dirname(os.path.realpath(__file__))

    def get_output(self, args, check_success=True):

        args.insert(0, "%s/../cli-to-spec" % self.path)

        # actually run cli-to-spec with the input
        code, stdout, stderr = pscheduler.run_program(args)

        if check_success:
            # make sure it succeeded
            self.assertEqual(code, 0)

        # get json out
        if code != 0:
            return stderr
        return json.loads(stdout)
        

    def test_all_options(self):

        # every option supported
        test_data =  {
            "--source": "10.0.0.1",
            "--source-node": "10.0.0.1",
            "--dest": "10.0.0.2",
            "--dest-node": "10.0.0.2",
            "--duration": "10",
            "-i": "1",
            "-u": True,
            "-b": "100000000",
            "--window-size": "64k",
            "--mss": "9000",
            "--buffer-length": "1600",
            "--ip-tos": "10",
            "--ip-version": "4",
            "--local-address": "10.0.0.1",
            "--omit": "5",
            "--no-delay": True,
            "--congestion": "reno",
            "--flow-label": "10",
            "--client-cpu-affinity": "1",
            "--server-cpu-affinity": "0",
            "--reverse": True
            }

        args = []

        for key, val in test_data.items():
            args.append(key)
            if type(val) != bool:
                args.append(val)

        data =self.get_output(args)

        # this is what we should get out
        checks = {
            'interval': 'PT1S', 
            'bandwidth': 100000000, 
            'client-cpu-affinity': 1,
            'duration': 'PT10S', 
            'ip-tos': 10,
            'mss': 9000,
            'source':'10.0.0.1',
            'ip-version': 6,
            'server-cpu-affinity': 0,
            'schema': 1, 
            'udp': True, 
            'local-address': '10.0.0.1', 
            'dest': '10.0.0.2', 
            'window-size': 64000, 
            'congestion': 'reno', 
            'no-delay': True, 
            'reverse': True, 
            'source-node': '10.0.0.1',
            'omit': 'PT5S', 
            'dest-node': '10.0.0.2', 
            'flow-label': 10, 
            'buffer-length': 1600
            }
            
        for key, val in checks.items():
            if key not in data.keys(): self.fail("Missing output key %s" % key) 
            self.assertEqual(val, data[key])


    def test_bandwidth_types(self):

        args = ["-b", "100M"]
        data = self.get_output(args)
        self.assertEqual(100 * 10**6, data['bandwidth'])

        args = ["-b", "10G"]
        data = self.get_output(args)
        self.assertEqual(10 * 10**9, data['bandwidth'])

        args = ["-b", "1000K"]
        data = self.get_output(args)
        self.assertEqual(1000 * 10**3, data['bandwidth'])
            

    def test_time(self):
        args = ["-t", "10"]
        data = self.get_output(args)
        self.assertEqual("PT10S", data['duration'])

        args = ["-t", "PT05M"]
        data = self.get_output(args)
        self.assertEqual("PT05M", data['duration'])


    def test_omit(self):
        args = ["-O", "10"]
        data = self.get_output(args)
        self.assertEqual("PT10S", data['omit'])

        args = ["-O", "PT05M"]
        data = self.get_output(args)
        self.assertEqual("PT05M", data['omit'])
        

    def test_bad_input(self):
        # unknown field
        args = ["--nope", "5"]
        data = self.get_output(args, check_success=False)
        self.assertEqual(data, "no such option: --nope\n")

        # bad type
        args = ["--bandwidth", "butterfly"]
        data = self.get_output(args, check_success=False)
        self.assertTrue("Invalid SI value" in data)


if __name__ == "__main__":
    unittest.main()
