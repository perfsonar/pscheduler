#!/usr/bin/python

import unittest
import pscheduler
import json
import os

class TestEnumerate(unittest.TestCase):
    
    path = os.path.dirname(os.path.realpath(__file__))

    def get_output(self, args, check_success=True):

        args.insert(0, "%s/../enumerate" % self.path)

        # actually run cli-to-spec with the input
        code, stdout, stderr = pscheduler.run_program(args)

        if check_success:
            # make sure it succeeded
            self.assertEqual(code, 0)

        # get json out
        if code != 0:
            return stderr
        return json.loads(stdout)


    def test_enumerate(self):
        data = self.get_output([])

        checks = {
            'maintainer': {
                'href': 'http://www.perfsonar.net', 
                'name': 'perfSONAR Development Team',
                'email': 'perfsonar-developer@internet2.edu',
                },
            'description': 'Measure network throughput between hosts', 
            'version': '1.0', 
            'scheduling-class': 'exclusive', 
            'schema': 1, 
            'name': 'throughput'
            }
            
        for key, val in checks.items():
            if key not in data.keys(): self.fail("Missing output key %s" % key) 
            self.assertEqual(val, data[key])


if __name__ == "__main__":
    unittest.main()
