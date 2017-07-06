"""
Helper classes for building unit tests
"""

import unittest

import json
import os
import sys
from pscheduler import run_program, json_validate
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
    def run_cmd(self, input, args=[], expected_status=0, json_out=True, expected_stderr=""):
        #Run command
        full_cmd = [self.cmd] + args
        try:
            status, stdout, stderr = run_program(full_cmd, stdin=input)
            print self.cmd
        except:
            #print stacktrace for any errors
            traceback.print_exc()
            self.fail("unable to run command {0}".format(self.cmd))
        
        #check stdout and stderr
        print stdout
        print stderr
        self.assertEqual(status, expected_status) #status should be 0
        if expected_status == 0:
            self.assertFalse(stderr) #stderr should be empty
        elif expected_stderr:
            self.assertEquals(stderr, expected_stderr)  
            
        if not json_out:
            return stdout
            
        #check for valid JSON
        try:
            result_json = json.loads(stdout)
        except:
            traceback.print_exc()
            self.fail("Invalid JSON returned by {0}: {1}".format(self.progname,stdout))
        
        return result_json
    
    def assert_cmd(self, input, args=[], expected_status=0, expected_valid=True, expected_errors=[], match_all_errors=True):
        #run command
        result_json = self.run_cmd(input, args=args, expected_status=expected_status)
        
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
Class for writing tests that spit out formatted non-json output
"""
class FormattedOutputUnitTest(ExecUnitTest):
    
    def assert_formatted_output(self, format, input, expected_status=0, expected_stdout=None, expected_stderr=None):
        output = self.run_cmd(input, args=[format], expected_status=expected_status, json_out=False, expected_stderr=expected_stderr)
        if expected_stdout:
            self.assertEquals(output.strip(), expected_stdout.strip())

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
        
        #validate JSON returned
        data_validator ={
            "type": "object",
            "properties": {
                "enum": { "$ref": "#/pScheduler/PluginEnumeration/Archiver" }
            },
            "additionalProperties": False,
            "required": ["enum"]
        }
        valid, error = json_validate({"enum": result_json}, data_validator)
        assert valid, error
        #verify name is as expected
        self.assertEqual(result_json['name'], self.name)

"""
Class for writing cli-to-spec unit tests
"""
class TestCliToSpecUnitTest(ExecUnitTest):
    progname = "cli-to-spec"
    
    """
    Given a map of CLI parameters and their values, check JSON. Assumes long names match
    JSON names if no option given. Entries can take a mix of the following forms:
    {
        "longname": {}, #boolean switch where longname is JSON key
        "longname": {"val": VALUE}, #switch with given value where longname is JSON key
        "longname": {"val": VALUE, "alt": "OPTIONAL_ALT_NAME"}, #use alternative command-line switch
        "longname": {"val": VALUE, "json_key": "JSON_KEY_NAME"}, # use different json name.
         "longname": {"val": VALUE, "json_key": None}, # skip checking in JSON
        "longname": {"val": VALUE, "json_val": "JSON_VAL"},# use different json val, if None, val will not be checked
    }
    """
    def assert_arg_map(self, arg_map):
        #build list of arguments
        args = []
        for arg in arg_map:
            #skip None 
            if arg_map[arg] is None:
                continue
            
            #determine if should use short or long form
            if "short" in arg_map[arg]:
                args.append("-{0}".format(arg_map[arg]["short"]))
            else:
                args.append("--{0}".format(arg))
            if "val" in arg_map[arg]:
                args.append(str(arg_map[arg]["val"]))
        
        #Run command
        result_json = self.run_cmd("", args=args)

        #should switch to assertIn for python 2.7
        for arg in arg_map:
            #look for json key
            json_key = arg
            if "json_key" in arg_map[arg]:
                json_key = arg_map[arg]["json_key"]
            if json_key is None:
                #allows you to skip result by setting to json_key = None
                continue
            else:
                assert(json_key in result_json)
            
            #look for value
            json_val = None
            if "json_val" in arg_map[arg]:
                json_val = arg_map[arg]["json_val"]
            elif "val" in arg_map[arg]:
                json_val = arg_map[arg]["val"]
            else:
                #assume boolean
                self.assertEquals(result_json[json_key], True)
                continue
            
            #If here, check value
            if json_val is None:
                #allows us to skip value checking by explicitly setting None
                continue
            else:
                self.assertEquals(str(result_json[json_key]), str(json_val))

"""
Class for writing test enumerate unit tests
"""
class TestEnumerateUnitTest(ExecUnitTest):
    progname = "enumerate"
    result_valid_field = "valid"
    scheduling_class = None #override this
    
    """
    Run enumerate command and verify output contain required fields
    """
    def test_enumerate_fields(self):
        #Run command
        result_json = self.run_cmd("")

        #validate JSON returned
        data_validator ={
            "type": "object",
            "properties": {
                "enum": { "$ref": "#/pScheduler/PluginEnumeration/Test" }
            },
            "additionalProperties": False,
            "required": ["enum"]
        }
        valid, error = json_validate({"enum": result_json}, data_validator)
        assert valid, error
        #verify name is as expected
        self.assertEqual(result_json['name'], self.name)
        #scheduling class is as expected
        self.assertEqual(result_json['scheduling-class'], self.scheduling_class)

"""
Class for writing limit-is-valid unit tests
"""
class TestLimitIsValidUnitTest(ExecUnitTest):
    progname = "limit-is-valid"
    result_valid_field = "valid"
    error_field = "message"

     
"""
Class for writing limit-passes unit tests
"""
class TestLimitPassesUnitTest(ExecUnitTest):
    progname = "limit-passes"
    result_valid_field = "passes"
    error_field = "errors"
    has_single_error = False

"""
Class for writing test participants unit tests
"""
class TestParticipantsUnitTest(ExecUnitTest):
    progname = "participants"
    
    def assert_participants(self, input, expected_participants, null_reason=""):
        result_json = self.run_cmd(input)
        assert("participants" in result_json)
        assert(len(result_json["participants"]), len(expected_participants))
        for i in range(0,len(expected_participants)):
            self.assertEquals(expected_participants[i], result_json["participants"][i])

        if null_reason:
            assert("null-reason" in result_json)
            self.assertEquals(null_reason, result_json["null-reason"])

"""
Class for writing test result-format unit tests
"""
class TestResultFormatUnitTest(FormattedOutputUnitTest):
    progname = "result-format"

"""
Class for writing test spec-format unit tests
"""
class TestSpecFormatUnitTest(FormattedOutputUnitTest):
    progname = "spec-format"
    
"""
Class for writing test spec-is-valid unit tests
"""
class TestSpecIsValidUnitTest(ExecUnitTest):
    progname = "spec-is-valid"
    result_valid_field = "valid"
        