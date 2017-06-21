"""
tests for the enumerate command.
"""

import unittest

import os
from pscheduler import run_program
import traceback
import json

class EnumerateTest(unittest.TestCase):
    name = 'esmond'
    
    """
    Run enumerate command and verify output
    """
    
    def test_enumerate(self):
        #find enumerate command
        enumerate_cmd = "../%s/enumerate" % self.name
        if __file__:
            enumerate_cmd = os.path.dirname(os.path.realpath(__file__)) + '/' + enumerate_cmd
        
        #Run command
        try:
            status, stdout, stderr = run_program([enumerate_cmd])
        except:
            #print stacktrace for any errors
            traceback.print_exc()
            self.fail("unable to run enumerate command %s" % (enumerate_cmd))
        
        #Check result
        self.assertEqual(status, 0) #status should be 0
        self.assertFalse(stderr) #stderr should be empty
        try:
            result_json = json.loads(stdout)
        except:
            traceback.print_exc()
            self.fail("Invalid JSON returned by enumerate: %s" % (stdout))
        #should switch to assertIn for python 2.7
        assert('schema' in result_json) 
        assert('name' in result_json)
        assert('description' in result_json)
        assert('version' in result_json)
        assert('maintainer' in result_json)
        assert('name' in result_json['maintainer'])
        assert('email' in result_json['maintainer'])
        assert('href' in result_json['maintainer'])
        #verify name is as expected
        self.assertEqual(result_json['name'], self.name)
        
if __name__ == '__main__':
    unittest.main()


