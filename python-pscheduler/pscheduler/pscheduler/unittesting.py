"""
Helper classes for building unit tests
"""

import unittest

import json
import os
import sys
from pscheduler import run_program
import traceback


"""
Base unit test class where a command is exec'd
"""
class ExecUnitTest(unittest.TestCase):
    name = None #this must be overriden
    progname = None #this must be overriden
    result_valid_field = "success"
    error_field = "error"
    has_single_error = True
    
    """
    Init command location
    """
    def __init__(self, *args, **kwargs):
        super(ExecUnitTest, self).__init__(*args, **kwargs)
        #find command
        cmd = "../{0}/{1}".format(self.name, self.progname)
        path = sys.modules[self.__module__].__file__
        if path:
            cmd = os.path.dirname(os.path.realpath(path)) + '/' + cmd
        self.cmd = cmd

    """
    Run and verify results
    """
    def run_cmd(self, input, expected_status=0):
        #Run command
        try:
            status, stdout, stderr = run_program([self.cmd], stdin=input)
            print self.cmd
        except:
            #print stacktrace for any errors
            traceback.print_exc()
            self.fail("unable to run command {0}".format(self.cmd))
        
        #check stdout and stderr
        print stdout
        print stderr
        self.assertEqual(status, expected_status) #status should be 0
        self.assertFalse(stderr) #stderr should be empty
        #check for valid JSON
        try:
            result_json = json.loads(stdout)
        except:
            traceback.print_exc()
            self.fail("Invalid JSON returned by {0}: {1}".format(self.progname,stdout))
        
        return result_json
    
    def assert_cmd(self, input, expected_status=0, expected_valid=True, expected_errors=[], match_all_errors=True):
        #run command
        result_json = self.run_cmd(input, expected_status=expected_status)
        
        #check fields
        assert(self.result_valid_field in result_json) 
        self.assertEqual(result_json[self.result_valid_field], expected_valid)
        if expected_valid:
            assert(self.error_field not in result_json) 
        else:
            assert(self.error_field in result_json) 
            if len(expected_errors) > 0 and match_all_errors:
                #verify list of errors same length
                if self.has_single_error:
                    self.assertEqual(1, len(expected_errors))
                else:
                    self.assertEqual(len(result_json[self.error_field]), len(expected_errors))
            for expected_error in expected_errors:
                #verify messages are in list
                if self.has_single_error:
                    self.assertEqual(result_json[self.error_field], expected_error)
                else:
                    assert(expected_error in result_json[self.error_field])

"""
Class for writing limit-passes unit tests
"""
class LimitPassesUnitTest(ExecUnitTest):
    progname = "limit-passes"
    result_valid_field = "passes"
    error_field = "errors"
    has_single_error = False

"""
Class for writing limit-is-valid unit tests
"""
class LimitIsValidUnitTest(ExecUnitTest):
    progname = "limit-is-valid"
    result_valid_field = "valid"
    error_field = "message"

"""
Class for writing archiver data-is-valid unit tests
"""
class ArchiverDataIsValidUnitTest(ExecUnitTest):
    progname = "data-is-valid"
    result_valid_field = "valid"
    
    """
Class for writing archiver enumerate unit tests
"""
class ArchiverEnumerateUnitTest(ExecUnitTest):
    progname = "enumerate"
    result_valid_field = "valid"
    
    """
    Run enumerate command and verify output contain required fields
    """
    def test_enumerate_fields(self):
        #Run command
        result_json = self.run_cmd("")
        
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
        