"""
Helper classes for building unit tests.

In general you will create subclasses of the classes included in this packages and
override the 'name' property with the name of your plug-in. Your unittest will then have
access to assert_* convenience methods and in some cases have default test cases run
automatically. See the individual classes for more details on options available.
"""

import unittest

import json
import os
import sys
import datetime
from pscheduler import run_program, json_validate, timedelta_as_iso8601, iso8601_as_timedelta, si_as_number, number_as_si
import traceback


#
# Base classes
#

class ExecUnitTest(unittest.TestCase):
    """
    Base unit test class where a command is exec'd. In general you will not instantiate this
    directly in your code and instead use one of its subclasses.
    """
    name = None #this must be overriden
    progname = None #this must be overriden
    result_valid_field = "success"
    error_field = "error"
    has_single_error = True
    
    
    def __init__(self, *args, **kwargs):
        """
        Init command location to ../$name/$progname relative to directory where test lives
        """
        super(ExecUnitTest, self).__init__(*args, **kwargs)
        #find command
        cmd = "../{0}/{1}".format(self.name, self.progname)
        path = sys.modules[self.__module__].__file__
        if path:
            cmd = os.path.dirname(os.path.realpath(path)) + '/' + cmd
        self.cmd = cmd

    def run_cmd(self, input, args=[], expected_status=0, json_out=True, expected_stderr=""):
        """
        Run and verify results. Takes following params:

        Args:
            input: a string to be fed via stdin to the program being executed
            args: optional command-line arguments to be given to the command-run.
            expected_status: the expected return code of the program. default is 0.
            json_out: indicates whether output should be expected to be valid JSON
            expected_stderr: string to match against stderr
    
        Returns:
            stdout as json dict if json_out is True (default), otehrwise a string
        """
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
        """
        Assert command that executes the command located at ../$name/$progname. It assumes 
        JSON output. It has the following options:
    
        Args:
            input: a string to be fed via stdin to the program being executed
            args: optional command-line arguments to be given to the command-run.
            expected_status: the expected return code of the program. default is 0.
            expected_errors: array of strings containing error messages expected to be seen in error_field
            match_all_errors: boolean indicating that expected_errors must be the only errors returned
        """
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


class FormattedOutputUnitTest(ExecUnitTest):
    """
    Class for writing tests that spit out formatted non-json output. In general you will not 
    instantiate this directly in your code and instead use one of its subclasses.
    """
    
    def assert_formatted_output(self, format, input, expected_status=0, expected_stdout=None, expected_stderr=None):
        output = self.run_cmd(input, args=[format], expected_status=expected_status, json_out=False, expected_stderr=expected_stderr)
        if expected_stdout:
            self.assertEquals(output.strip(), expected_stdout.strip())

#
# Archiver plugin classes
#

class ArchiverDataIsValidUnitTest(ExecUnitTest):
    """
    Class for writing archiver data-is-valid unit tests
    """
    progname = "data-is-valid"
    result_valid_field = "valid"
    

class ArchiverEnumerateUnitTest(ExecUnitTest):
    """
    Class for writing archiver enumerate unit tests. The most common case will be to
    create a subclass and override the "name" property with the name of the archiver plug-in.
    """
    progname = "enumerate"
    result_valid_field = "valid"
    
    def test_enumerate_fields(self):
        """
        Unit test to verify enumumerate execures, returns valid JSON with required fields, and
        verifies the 'name' field in the JSON matches the 'name' property of this class
        """
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

#
# Test plugin classes
#

class TestCliToSpecUnitTest(ExecUnitTest):
    """
    Class for writing test plug-in cli-to-spec unit tests. Doe snot include additional tests 
    by default, but does provide helper assert method for writing your own test cases. 
    """
    progname = "cli-to-spec"
    
    def assert_arg_map(self, arg_map):
        """
        check JSON given arg_map, a dict of CLI parameters and their values. 
        
        Args:
            argmap: dict assuming long names (the dict key) match JSON names if no option 
            given. arg_map can take a mix of the following forms:
                {
                    "longname": {}, #boolean switch where longname is JSON key
                    "longname": {"val": VALUE}, #switch with given value where longname is JSON key
                    "longname": {"val": VALUE, "short": "OPTIONAL_ALT_NAME"}, #use alternative command-line switch
                    "longname": {"val": VALUE, "json_key": "JSON_KEY_NAME"}, # use different json name.
                    "longname": {"val": VALUE, "json_key": None}, # skip checking in JSON
                    "longname": {"val": VALUE, "json_val": "JSON_VAL"},# use different json val, if None, val will not be checked
                }
        """
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

class TestEnumerateUnitTest(ExecUnitTest):
    """
    Class for writing test enumerate unit tests. Need to override name and scheduling_class
    """
    progname = "enumerate"
    result_valid_field = "valid"
    scheduling_class = None #override this
    

    def test_enumerate_fields(self):
        """
        Run enumerate command, verify is valid JSON, output contain required fields and
        the JSON "name" and "scheduling-class" fields match this classes properties
        """
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


class TestLimitIsValidUnitTest(ExecUnitTest):
    """
    Class for writing test plug-in limit-is-valid unit tests
    """
    progname = "limit-is-valid"
    result_valid_field = "valid"
    error_field = "message"

     

class TestLimitPassesUnitTest(ExecUnitTest):
    """
    Class for writing test plug-in limit-passes unit tests
    """
    progname = "limit-passes"
    result_valid_field = "passes"
    error_field = "errors"
    has_single_error = False
    
    def assert_numeric_limit(self, field, label, lower, upper):
        """
        Assert command that performs basic checks on a numeric limit. It checks value
        within the provided bounds, above and below the provided bounds, the unspecified 
        case and the invert option.
    
        Args:
            field: the name of the limit to test
            label: the human-readable name used in error messages
            lower: the lower bound of the limit to check as number
            upper: the upper bound of the limit to check as number
        """
        ##in range
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {1}}}}}'.format(field, upper, lower))
        ##out of range
        expected_errors = ["{0} not in {1}..{2}".format(label, lower, upper)]
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {3}}}}}'.format(field, upper, lower, upper+1), expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {3}}}}}'.format(field, upper, lower, lower-1), expected_valid=False, expected_errors=expected_errors)
        ##not specified
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{}}}}'.format(field, upper, lower))
        ##invert
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {1}}}}}'.format(field, upper, lower), expected_valid=False)
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {3}}}}}'.format(field, upper, lower, upper+1))
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {3}}}}}'.format(field, upper, lower, lower-1))
    
    def assert_sinumber_limit(self, field, label, lower, upper):
        """
        Assert command that performs basic checks on a limit defined with SI numbers. 
        It checks value within the provided bounds, above/below the provided bounds, 
        the unspecified case and the invert option.
    
        Args:
            field: the name of the limit to test
            label: the human-readable name used in error messages
            lower: the lower bound of the limit to check as SI number string
            upper: the upper bound of the limit to check as SI number string
        """
        above_range = number_as_si(si_as_number(upper) * 2)
        below_range = number_as_si(si_as_number(lower) / 2)
        ##in range
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{"{0}": "{1}"}}}}'.format(field, upper, lower))
        ##out of range
        expected_errors = ["{0} not in {1}..{2}".format(label, lower, upper)]
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{"{0}": "{3}"}}}}'.format(field, upper, lower, above_range), expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{"{0}": "{3}"}}}}'.format(field, upper, lower, below_range), expected_valid=False, expected_errors=expected_errors)
        ##not specified
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{}}}}'.format(field, upper, lower))
        ##invert
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{"{0}": "{1}"}}}}'.format(field, upper, lower), expected_valid=False)
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{"{0}": "{3}"}}}}'.format(field, upper, lower, above_range))
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{"{0}": "{3}"}}}}'.format(field, upper, lower, below_range))
        
    def assert_numeric_list_limit(self, field, label): 
        """
        Assert command that performs basic checks on a limit defined as a list of numbers. 
        It uses a static set of bounds and tests cases in range, out of range, using the 
        invert option and the fail-message option.
    
        Args:
            field: the name of the limit to test
            label: the human-readable name used in error messages
        """
        ##in range
        self.assert_cmd('{{"limit": {{"{0}": {{"match": [1, 2, 3]}}}}, "spec": {{"{0}": 1}}}}'.format(field)) #first
        self.assert_cmd('{{"limit": {{"{0}": {{"match": [1, 2, 3]}}}}, "spec": {{"{0}": 2}}}}'.format(field)) #middle
        self.assert_cmd('{{"limit": {{"{0}": {{"match": [1, 2, 3]}}}}, "spec": {{"{0}": 3}}}}'.format(field)) #last
        self.assert_cmd('{{"limit": {{"{0}": {{"match": [1, 2, 3]}}}}, "spec": {{}}}}'.format(field))
        ##out of range
        expected_errors = ["{0} not within limit".format(label)]
        self.assert_cmd('{{"limit": {{"{0}": {{"match": [1, 2, 3]}}}}, "spec": {{"{0}": 4}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{{"limit": {{"{0}": {{"match": [1, 2, 3]}}}}, "spec": {{"{0}": 0}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
        ##invert
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true, "match": [1, 2, 5]}}}}, "spec": {{"{0}": 4}}}}'.format(field))
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true, "match": [1, 2, 3]}}}}, "spec": {{"{0}": 1}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
        ##with fail-message
        expected_errors = ["Test message"]
        self.assert_cmd('{{"limit": {{"{0}": {{"match": [1, 2, 3], "fail-message": "Test message"}}}}, "spec": {{"{0}": 4}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{{"limit": {{"{0}": {{"match": [1, 2, 5], "fail-message": "Test message"}}}}, "spec": {{"{0}": 4}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
    
    def assert_numeric_range_limit(self, field, label, lower, upper):
        """
        Assert command that performs basic checks on a numeric limit where the spec field 
        is a range (as opposed to a single number). It checks value within the provided 
        bounds, above/below the provided bounds, the unspecified case and the invert 
        option.
    
        Args:
            field: the name of the limit to test
            label: the human-readable name used in error messages
            lower: the lower bound of the limit to check as number
            upper: the upper bound of the limit to check as number
        """
        ##in range
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {{"upper": {1}, "lower": {2}}}}}}}'.format(field, upper, lower))
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {{"upper": {3}, "lower": {4}}}}}}}'.format(field, upper, lower, upper-1, lower+1))
        ##out of range
        expected_error_lower = ["{0} (lower bound) not in {1}..{2}".format(label, lower, upper)]
        expected_error_upper = ["{0} (upper bound) not in {1}..{2}".format(label, lower, upper)]
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {{"upper": {2}, "lower": {3}}}}}}}'.format(field, upper, lower, lower-1), expected_valid=False, expected_errors=expected_error_lower)
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {{"upper": {3}, "lower": {1}}}}}}}'.format(field, upper, lower, upper+1), expected_valid=False, expected_errors=expected_error_upper)
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {{"upper": {3}, "lower": {4}}}}}}}'.format(field, upper, lower, upper+2, upper+1), expected_valid=False, expected_errors=expected_error_upper+expected_error_lower)
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {{"upper": {3}, "lower": {4}}}}}}}'.format(field, upper, lower, lower-1, lower-2), expected_valid=False, expected_errors=expected_error_upper+expected_error_lower)
        ##not specified
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{}}}}'.format(field, upper, lower))
        ##invert
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {{"upper": {3}, "lower": {4}}}}}}}'.format(field, upper, lower, upper-1, lower+1), expected_valid=False)
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {{"upper": {2}, "lower": {3}}}}}}}'.format(field, upper, lower, lower-1), expected_valid=False)
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {{"upper": {3}, "lower": {1}}}}}}}'.format(field, upper, lower, upper+1), expected_valid=False)
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {{"upper": {3}, "lower": {4}}}}}}}'.format(field, upper, lower, upper+2, upper+1))
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": {1}, "lower": {2}}}}}}}, "spec": {{"{0}": {{"upper": {3}, "lower": {4}}}}}}}'.format(field, upper, lower, lower-1, lower-2))
        
    def assert_boolean_limit(self, field, label): 
        """
        Assert command that performs basic checks on boolean limits. Tests all combinations
        of true and false and also checks cases where value is not specified or a 
        fail-message is provided.
    
        Args:
            field: the name of the limit to test
            label: the human-readable name used in error messages
        """
        ##in range
        self.assert_cmd('{{"limit": {{"{0}": {{"match": true}}}}, "spec": {{"{0}": true}}}}'.format(field))
        self.assert_cmd('{{"limit": {{"{0}": {{"match": false}}}}, "spec": {{"{0}": false}}}}'.format(field))
        self.assert_cmd('{{"limit": {{"{0}": {{"match": false}}}}, "spec": {{}}}}'.format(field))
        ##out of range
        expected_errors = ["{0} testing not allowed".format(label)]
        self.assert_cmd('{{"limit": {{"{0}": {{"match": true}}}}, "spec": {{"{0}": false}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{{"limit": {{"{0}": {{"match": false}}}}, "spec": {{"{0}": true}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
        ###not specified
        self.assert_cmd('{{"limit": {{"{0}": {{"match": true}}}}, "spec": {{}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
        ##with fail-message
        expected_errors = ["Test message"]
        self.assert_cmd('{{"limit": {{"{0}": {{"match": true, "fail-message": "Test message"}}}}, "spec": {{"{0}": false}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{{"limit": {{"{0}": {{"match": false, "fail-message": "Test message"}}}}, "spec": {{"{0}": true}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
        ###not specified
        self.assert_cmd('{{"limit": {{"{0}": {{"match": true, "fail-message": "Test message"}}}}, "spec": {{}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)

    def assert_duration_limit(self, field, label, lower, upper):
        """
        Assert command that performs basic checks on a duration limit specified as ISO8601
        durations. Test combinations of in range, out of range, unspecified and use of 
        invert.
        
        Args:
            field: the name of the limit to test
            label: the human-readable name used in error messages
            lower: the lower bound of the limit to check as ISO8601
            upper: the upper bound of the limit to check as ISO8601
        """
        below_range = timedelta_as_iso8601(iso8601_as_timedelta(lower) - datetime.timedelta(seconds=1))
        above_range = timedelta_as_iso8601(iso8601_as_timedelta(upper) + datetime.timedelta(seconds=1))
        ##in range
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{"{0}": "{1}"}}}}'.format(field, upper, lower))
        ##out of range
        expected_errors = ["{0} not in {1}..{2}".format(label, lower, upper)]
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{"{0}": "{3}"}}}}'.format(field, upper, lower, above_range), expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{"{0}": "{3}"}}}}'.format(field, upper, lower, below_range), expected_valid=False, expected_errors=expected_errors)
        ##not specified
        self.assert_cmd('{{"limit": {{"{0}": {{"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{}}}}'.format(field, upper, lower))
        ##invert
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{"{0}": "{1}"}}}}'.format(field, upper, lower), expected_valid=False)
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{"{0}": "{3}"}}}}'.format(field, upper, lower, above_range))
        self.assert_cmd('{{"limit": {{"{0}": {{"invert": true,"range": {{"upper": "{1}", "lower": "{2}"}}}}}}, "spec": {{"{0}": "{3}"}}}}'.format(field, upper, lower, below_range))

    def assert_string_limit(self, field, label):
        """
        Assert command that performs basic checks on a string limit. Uses default strings 
        to test in range, out of range, unspecified, invert and fail-message. 
        
        Args:
            field: the name of the limit to test
            label: the human-readable name used in error messages
        """
        ##in range
        self.assert_cmd('{{"limit": {{"{0}": {{"match": {{"style":"exact", "match": "foo"}} }}}}, "spec": {{"{0}": "foo"}}}}'.format(field))
        self.assert_cmd('{{"limit": {{"{0}": {{"match": {{"style":"regex", "match": "fo.*"}} }}}}, "spec": {{"{0}": "foo"}}}}'.format(field))
        self.assert_cmd('{{"limit": {{"{0}": {{"match": {{"style":"contains", "match": "oo"}} }}}}, "spec": {{"{0}": "foo"}}}}'.format(field))
        ##out of range
        expected_errors = ["{0} does not match limit".format(label)]
        self.assert_cmd('{{"limit": {{"{0}": {{"match": {{"style":"exact", "match": "foo"}} }}}}, "spec": {{"{0}": "bar"}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
        ##invert
        self.assert_cmd('{{"limit": {{"{0}": {{"match": {{"invert": true, "style":"exact", "match": "foo"}} }}}}, "spec": {{"{0}": "bar"}}}}'.format(field))
        self.assert_cmd('{{"limit": {{"{0}": {{"match": {{"invert": true, "style":"exact", "match": "foo"}} }}}}, "spec": {{"{0}": "foo"}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
        ##fail-msg
        expected_errors = ["Test message"]
        self.assert_cmd('{{"limit": {{"{0}": {{"match": {{"style":"exact", "match": "foo"}}, "fail-message": "Test message"}}}}, "spec": {{"{0}": "bar"}}}}'.format(field), expected_valid=False, expected_errors=expected_errors)
        
    def assert_ip_version_limit(self): 
        """
        Assert command that performs basic checks on the ip-version field. Test lots of
        combinations of 4 and 6, in range, out of range, unspecified and inverted.
        """
        ##in range
        self.assert_cmd('{"limit": {"ip-version": {"enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "ip-version": 4, "schema": 1}}')
        self.assert_cmd('{"limit": {"ip-version": {"enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "ip-version": 6, "schema": 1}}')
        self.assert_cmd('{"limit": {"ip-version": {"enumeration": [4]}}, "spec": {"dest": "psched-dev1", "ip-version": 4, "schema": 1}}')
        self.assert_cmd('{"limit": {"ip-version": {"enumeration": [6]}}, "spec": {"dest": "psched-dev1", "ip-version": 6, "schema": 1}}')
        ##out of range
        expected_errors = ["IP Version IPv7 is not allowed"]
        self.assert_cmd('{"limit": {"ip-version": {"enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "ip-version": 7, "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{"limit": {"ip-version": {"enumeration": [4]}}, "spec": {"dest": "psched-dev1", "ip-version": 6, "schema": 1}}', expected_valid=False)
        self.assert_cmd('{"limit": {"ip-version": {"enumeration": [6]}}, "spec": {"dest": "psched-dev1", "ip-version": 4, "schema": 1}}', expected_valid=False)
        ##not specified
        self.assert_cmd('{"limit": {"ip-version": {"enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        self.assert_cmd('{"limit": {"ip-version": {"enumeration": [4]}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        self.assert_cmd('{"limit": {"ip-version": {"enumeration": [6]}}, "spec": {"dest": "psched-dev1", "schema": 1}}')
        ##invert
        self.assert_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "ip-version": 4, "schema": 1}}', expected_valid=False)
        self.assert_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "ip-version": 6, "schema": 1}}', expected_valid=False)
        self.assert_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [4]}}, "spec": {"dest": "psched-dev1", "ip-version": 4, "schema": 1}}', expected_valid=False)
        self.assert_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [4]}}, "spec": {"dest": "psched-dev1", "ip-version": 6, "schema": 1}}')
        self.assert_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [4, 6]}}, "spec": {"dest": "psched-dev1", "ip-version": 7, "schema": 1}}')
        self.assert_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [4]}}, "spec": {"dest": "psched-dev1", "ip-version": 6, "schema": 1}}')
        self.assert_cmd('{"limit": {"ip-version": {"invert": true, "enumeration": [6]}}, "spec": {"dest": "psched-dev1", "ip-version": 4, "schema": 1}}')

    def assert_endpoint_limits(self):
        """
        Assert command that performs basic checks the source, dest and endpoint limits
        present in many point-topoint tests. In particular it checks numerous combinations
        of IPv4 and IPv6 including hostnames with different combinations of A and AAAA
        records. NOTE: This functioning requires DNS to be functioning properly. It also 
        relies on static DNS names that if they go away or the underlying IPs change will 
        need to be updated. Not ideal but is the easiest way to test some really common 
        cases that are common sources of bugs. 
        """
        #########################
        #check source
        #########################
        error_unallowed_range = "{0} is not in the allowed address range"
        error_ip_mismatch = "source {0} and dest {1} cannot be resolved to IP addresses of the same type"

        ###no source specified
        expected_errors = ["This test has a limit on the source field but the source was not specifed. You must specify a source to run this test"]
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.129.254.38/32"]}}, "spec": {"dest": "lbl-pt1.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)

        ### v4 source, v4 dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.128.151.25/32"]}}, "spec": {"source": "198.128.151.25", "dest": "198.129.254.38", "schema": 1}}')
        ### v4 source, v6 dest
        expected_errors = [error_ip_mismatch.format('198.128.151.25', '2001:400:501:1150::3')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.128.151.25/32"]}}, "spec": {"source": "198.128.151.25", "dest": "2001:400:501:1150::3", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### v4 source, A only dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.128.151.25/32"]}}, "spec": {"source": "198.128.151.25", "dest": "sacr-pt1-v4.es.net", "schema": 1}}')
        ### v4 source, AAAA only dest
        expected_errors = [error_ip_mismatch.format('198.128.151.25', 'sacr-pt1-v6.es.net')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.128.151.25/32"]}}, "spec": {"source": "198.128.151.25", "dest": "sacr-pt1-v6.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### v4 source, A and AAAA only dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.128.151.25/32"]}}, "spec": {"source": "198.128.151.25", "dest": "sacr-pt1.es.net", "schema": 1}}')
        
        ### v6 source, v4 dest
        expected_errors = [error_ip_mismatch.format('2001:400:210:151::25', '198.129.254.38')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"source": "2001:400:210:151::25", "dest": "198.129.254.38", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### v6 source, v6 dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"source": "2001:400:210:151::25", "dest": "2001:400:501:1150::3", "schema": 1}}')
        ### v6 source, A only dest
        expected_errors = [error_ip_mismatch.format('2001:400:210:151::25', 'sacr-pt1-v4.es.net')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"source": "2001:400:210:151::25", "dest": "sacr-pt1-v4.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### v6 source, AAAA only dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"source": "2001:400:210:151::25", "dest": "sacr-pt1-v6.es.net", "schema": 1}}')
        ### v6 source, A and AAAA only dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"source": "2001:400:210:151::25", "dest": "sacr-pt1.es.net", "schema": 1}}')
        
        ### A-only source, v4 dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.129.254.30/32"]}}, "spec": {"source": "lbl-pt1-v4.es.net", "dest": "198.129.254.38", "schema": 1}}')
        ### A-only source, v6 dest
        expected_errors = [error_ip_mismatch.format('lbl-pt1-v4.es.net', '2001:400:501:1150::3')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.129.254.30/32"]}}, "spec": {"source": "lbl-pt1-v4.es.net", "dest": "2001:400:501:1150::3", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### A-only source, A only dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.129.254.30/32"]}}, "spec": {"source": "lbl-pt1-v4.es.net", "dest": "sacr-pt1-v4.es.net", "schema": 1}}')
        ### A-only source, AAAA only dest
        expected_errors = [error_ip_mismatch.format('lbl-pt1-v4.es.net', 'sacr-pt1-v6.es.net')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.129.254.30/32"]}}, "spec": {"source": "lbl-pt1-v4.es.net", "dest": "sacr-pt1-v6.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### A-only source, A and AAAA only dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.129.254.30/32"]}}, "spec": {"source": "lbl-pt1-v4.es.net", "dest": "sacr-pt1.es.net", "schema": 1}}')
        
        ### AAAA-only source, v4 dest
        expected_errors = [error_ip_mismatch.format('lbl-pt1-v6.es.net', '198.129.254.38')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:201:1150::3/32"]}}, "spec": {"source": "lbl-pt1-v6.es.net", "dest": "198.129.254.38", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### AAAA-only source, v6 dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:201:1150::3/32"]}}, "spec": {"source": "lbl-pt1-v6.es.net", "dest": "2001:400:501:1150::3", "schema": 1}}')
        ### AAAA-only source, A only dest
        expected_errors = [error_ip_mismatch.format('lbl-pt1-v6.es.net', 'sacr-pt1-v4.es.net')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:201:1150::3/32"]}}, "spec": {"source": "lbl-pt1-v6.es.net", "dest": "sacr-pt1-v4.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### AAAA-only source, AAAA only dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:201:1150::3/32"]}}, "spec": {"source": "lbl-pt1-v6.es.net", "dest": "sacr-pt1-v6.es.net", "schema": 1}}')
        ### AAAA-only source, A and AAAA only dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:201:1150::3/32"]}}, "spec": {"source": "lbl-pt1-v6.es.net", "dest": "sacr-pt1.es.net", "schema": 1}}')

        ### A+AAAA source, v4 dest
        expected_errors = [error_unallowed_range.format('198.128.151.25')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"source": "antg-staging.es.net", "dest": "198.129.254.38", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.128.151.25/32"]}}, "spec": {"source": "antg-staging.es.net", "dest": "198.129.254.38", "schema": 1}}')
        ### A+AAAA source, v6 dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"source": "antg-staging.es.net", "dest": "2001:400:501:1150::3", "schema": 1}}')
        expected_errors = [error_unallowed_range.format('2001:400:210:151::25')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.128.151.25/32"]}}, "spec": {"source": "antg-staging.es.net", "dest": "2001:400:501:1150::3", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### A+AAAA source, A only dest
        expected_errors = [error_unallowed_range.format('198.128.151.25')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"source": "antg-staging.es.net", "dest": "sacr-pt1-v4.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.128.151.25/32"]}}, "spec": {"source": "antg-staging.es.net", "dest": "sacr-pt1-v4.es.net", "schema": 1}}')
        ### A+AAAA source, AAAA only dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"source": "antg-staging.es.net", "dest": "sacr-pt1-v6.es.net", "schema": 1}}')
        expected_errors = [error_unallowed_range.format('2001:400:210:151::25')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.128.151.25/32"]}}, "spec": {"source": "antg-staging.es.net", "dest": "sacr-pt1-v6.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### A+AAAA source, A and AAAA only dest
        self.assert_cmd('{"limit": {"source": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"source": "antg-staging.es.net", "dest": "sacr-pt1.es.net", "schema": 1}}')
        expected_errors = [error_unallowed_range.format('2001:400:210:151::25')]
        self.assert_cmd('{"limit": {"source": {"cidr": ["198.128.151.25/32"]}}, "spec": {"source": "antg-staging.es.net", "dest": "sacr-pt1.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        
        ##test invert
        self.assert_cmd('{"limit": {"source": {"invert": true, "cidr": ["198.128.151.25/32"]}}, "spec": {"source": "198.128.151.26", "dest": "198.129.254.38", "schema": 1}}')
        
        #########################
        #check dest w/ source
        #########################
        error_unallowed_range = "{0} is not in the allowed address range"
        error_ip_mismatch = "source {1} and dest {0} cannot be resolved to IP addresses of the same type"

        ### v4 dest, v4 source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "198.128.151.25", "source": "198.129.254.38", "schema": 1}}')
        ### v4 dest, v6 source
        expected_errors = [error_ip_mismatch.format('198.128.151.25', '2001:400:501:1150::3')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "198.128.151.25", "source": "2001:400:501:1150::3", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### v4 dest, A only source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "198.128.151.25", "source": "sacr-pt1-v4.es.net", "schema": 1}}')
        ### v4 dest, AAAA only source
        expected_errors = [error_ip_mismatch.format('198.128.151.25', 'sacr-pt1-v6.es.net')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "198.128.151.25", "source": "sacr-pt1-v6.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### v4 dest, A and AAAA only source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "198.128.151.25", "source": "sacr-pt1.es.net", "schema": 1}}')
        
        ### v6 dest, v4 source
        expected_errors = [error_ip_mismatch.format('2001:400:210:151::25', '198.129.254.38')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"dest": "2001:400:210:151::25", "source": "198.129.254.38", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### v6 dest, v6 source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"dest": "2001:400:210:151::25", "source": "2001:400:501:1150::3", "schema": 1}}')
        ### v6 dest, A only source
        expected_errors = [error_ip_mismatch.format('2001:400:210:151::25', 'sacr-pt1-v4.es.net')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"dest": "2001:400:210:151::25", "source": "sacr-pt1-v4.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### v6 dest, AAAA only source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"dest": "2001:400:210:151::25", "source": "sacr-pt1-v6.es.net", "schema": 1}}')
        ### v6 dest, A and AAAA only source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"dest": "2001:400:210:151::25", "source": "sacr-pt1.es.net", "schema": 1}}')
        
        ### A-only dest, v4 source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.30/32"]}}, "spec": {"dest": "lbl-pt1-v4.es.net", "source": "198.129.254.38", "schema": 1}}')
        ### A-only dest, v6 source
        expected_errors = [error_ip_mismatch.format('lbl-pt1-v4.es.net', '2001:400:501:1150::3')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.30/32"]}}, "spec": {"dest": "lbl-pt1-v4.es.net", "source": "2001:400:501:1150::3", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### A-only dest, A only source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.30/32"]}}, "spec": {"dest": "lbl-pt1-v4.es.net", "source": "sacr-pt1-v4.es.net", "schema": 1}}')
        ### A-only dest, AAAA only source
        expected_errors = [error_ip_mismatch.format('lbl-pt1-v4.es.net', 'sacr-pt1-v6.es.net')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.30/32"]}}, "spec": {"dest": "lbl-pt1-v4.es.net", "source": "sacr-pt1-v6.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### A-only dest, A and AAAA only source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.30/32"]}}, "spec": {"dest": "lbl-pt1-v4.es.net", "source": "sacr-pt1.es.net", "schema": 1}}')
        
        ### AAAA-only dest, v4 source
        expected_errors = [error_ip_mismatch.format('lbl-pt1-v6.es.net', '198.129.254.38')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:201:1150::3/32"]}}, "spec": {"dest": "lbl-pt1-v6.es.net", "source": "198.129.254.38", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### AAAA-only dest, v6 source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:201:1150::3/32"]}}, "spec": {"dest": "lbl-pt1-v6.es.net", "source": "2001:400:501:1150::3", "schema": 1}}')
        ### AAAA-only dest, A only source
        expected_errors = [error_ip_mismatch.format('lbl-pt1-v6.es.net', 'sacr-pt1-v4.es.net')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:201:1150::3/32"]}}, "spec": {"dest": "lbl-pt1-v6.es.net", "source": "sacr-pt1-v4.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### AAAA-only dest, AAAA only source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:201:1150::3/32"]}}, "spec": {"dest": "lbl-pt1-v6.es.net", "source": "sacr-pt1-v6.es.net", "schema": 1}}')
        ### AAAA-only dest, A and AAAA only source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:201:1150::3/32"]}}, "spec": {"dest": "lbl-pt1-v6.es.net", "source": "sacr-pt1.es.net", "schema": 1}}')

        ### A+AAAA dest, v4 source
        expected_errors = [error_unallowed_range.format('198.128.151.25')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"dest": "antg-staging.es.net", "source": "198.129.254.38", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "antg-staging.es.net", "source": "198.129.254.38", "schema": 1}}')
        ### A+AAAA dest, v6 source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"dest": "antg-staging.es.net", "source": "2001:400:501:1150::3", "schema": 1}}')
        expected_errors = [error_unallowed_range.format('2001:400:210:151::25')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "antg-staging.es.net", "source": "2001:400:501:1150::3", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### A+AAAA dest, A only source
        expected_errors = [error_unallowed_range.format('198.128.151.25')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"dest": "antg-staging.es.net", "source": "sacr-pt1-v4.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "antg-staging.es.net", "source": "sacr-pt1-v4.es.net", "schema": 1}}')
        ### A+AAAA dest, AAAA only source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"dest": "antg-staging.es.net", "source": "sacr-pt1-v6.es.net", "schema": 1}}')
        expected_errors = [error_unallowed_range.format('2001:400:210:151::25')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "antg-staging.es.net", "source": "sacr-pt1-v6.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ### A+AAAA dest, A and AAAA only source
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:210:151::25/128"]}}, "spec": {"dest": "antg-staging.es.net", "source": "sacr-pt1.es.net", "schema": 1}}')
        expected_errors = [error_unallowed_range.format('2001:400:210:151::25')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "antg-staging.es.net", "source": "sacr-pt1.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        
        ##test invert
        self.assert_cmd('{"limit": {"dest": {"invert": true, "cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "198.128.151.26", "source": "198.129.254.38", "schema": 1}}')
        
        #########################
        #check dest w/o source
        #########################
        error_unallowed_range = "{0} is not in the allowed address range"
        
        #v4 limit
        ##v4 dest
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.38/32"]}}, "spec": {"dest": "198.129.254.38", "schema": 1}}')
        ##v6 dest
        expected_errors = [error_unallowed_range.format('2001:400:501:1150::3')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.38/32"]}}, "spec": {"dest": "2001:400:501:1150::3", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##A-only dest
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.38/32"]}}, "spec": {"dest": "sacr-pt1-v4.es.net", "schema": 1}}')
        ##AAAA-only dest
        expected_errors = [error_unallowed_range.format('2001:400:501:1150::3')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.38/32"]}}, "spec": {"dest": "sacr-pt1-v6.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##A+AAAA dest
        ### this should fail. both addresses need to be in range.
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.38/32"]}}, "spec": {"dest": "sacr-pt1.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)

        #v6 limit
        ##v4 dest
        expected_errors = [error_unallowed_range.format('198.129.254.38')]
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:501:1150::3/128"]}}, "spec": {"dest": "198.129.254.38", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##v6 dest
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:501:1150::3/128"]}}, "spec": {"dest": "2001:400:501:1150::3", "schema": 1}}')
        ##A-only dest
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:501:1150::3/128"]}}, "spec": {"dest": "sacr-pt1-v4.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        ##AAAA-only dest
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:501:1150::3/128"]}}, "spec": {"dest": "sacr-pt1-v6.es.net", "schema": 1}}')
        ##A+AAAA dest
        ### this should fail. both addresses need to be in range.
        self.assert_cmd('{"limit": {"dest": {"cidr": ["2001:400:501:1150::3/128"]}}, "spec": {"dest": "sacr-pt1.es.net", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        
        #v4+v6 limit (all should pass)
        ##v4 dest
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.38/32", "2001:400:501:1150::3/128"]}}, "spec": {"dest": "198.129.254.38", "schema": 1}}')
        ##v6 dest
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.38/32", "2001:400:501:1150::3/128"]}}, "spec": {"dest": "2001:400:501:1150::3", "schema": 1}}')
        ##A-only dest
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.38/32", "2001:400:501:1150::3/128"]}}, "spec": {"dest": "sacr-pt1-v4.es.net", "schema": 1}}')
        ##AAAA-only dest
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.38/32", "2001:400:501:1150::3/128"]}}, "spec": {"dest": "sacr-pt1-v6.es.net", "schema": 1}}')
        ##A+AAAA dest
        self.assert_cmd('{"limit": {"dest": {"cidr": ["198.129.254.38/32", "2001:400:501:1150::3/128"]}}, "spec": {"dest": "sacr-pt1.es.net", "schema": 1}}')

        #########################
        # check endpoint
        #########################
        ### minimize testing because code heavily exercised in previous tests. 
        ### Just need to test OR condition

        ##works
        self.assert_cmd('{"limit": {"endpoint": {"cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "198.128.151.25", "source": "198.129.254.38", "schema": 1}}')
        self.assert_cmd('{"limit": {"endpoint": {"cidr": ["198.128.151.25/32"]}}, "spec": {"source": "198.128.151.25", "dest": "198.129.254.38", "schema": 1}}')
        self.assert_cmd('{"limit": {"endpoint": {"cidr": ["198.128.151.25/32"]}}, "spec": {"dest": "198.128.151.25", "schema": 1}}')
        
        #fails 
        expected_errors = ["source nor dest matches the IP range set by endpoint limit"]
        self.assert_cmd('{"limit": {"endpoint": {"cidr": ["198.128.151.26/32"]}}, "spec": {"dest": "198.128.151.25", "source": "198.129.254.38", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
        self.assert_cmd('{"limit": {"endpoint": {"cidr": ["198.128.151.26/32"]}}, "spec": {"dest": "198.128.151.25", "schema": 1}}', expected_valid=False, expected_errors=expected_errors)
  

class TestParticipantsUnitTest(ExecUnitTest):
    """
    Class for writing test plug-in participants unit tests
    """
    progname = "participants"
    
    def assert_participants(self, input, expected_participants, null_reason=""):
        """
        Asserts the participants returned by command match expected list. params are:
        
        Args:
            input: valid JSON string
            expected_participants: array of strings of expected participants
            null_reason: optional string that must match against the null-reason field
        """
        result_json = self.run_cmd(input)
        assert("participants" in result_json)
        assert(len(result_json["participants"]), len(expected_participants))
        for i in range(0,len(expected_participants)):
            self.assertEquals(expected_participants[i], result_json["participants"][i])

        if null_reason:
            assert("null-reason" in result_json)
            self.assertEquals(null_reason, result_json["null-reason"])

class TestResultFormatUnitTest(FormattedOutputUnitTest):
    """
    Class for writing test plug-in result-format unit tests
    """
    progname = "result-format"

class TestSpecFormatUnitTest(FormattedOutputUnitTest):
    """
    Class for writing test plug-in spec-format unit tests
    """
    progname = "spec-format"
    

class TestSpecIsValidUnitTest(ExecUnitTest):
    """
    Class for writing test plug-in spec-is-valid unit tests
    """
    progname = "spec-is-valid"
    result_valid_field = "valid"

class TestSpecToCliUnitTest(ExecUnitTest):
    """
    Class for writing test plug-in spec-to-cli unit tests
    """
    progname = "spec-to-cli"
    
    def assert_spec_to_cli(self, input, expected_cli_args):
        """
        Run spec-to-cli and verify list of options matches provided map
        
        Args:
            input: JSON string of test-spec
            expected_cli_args: A dict of the form:
                {
                    "cli-opt": "value" #if value none then assumed to be switch
                }
        """
        #run command
        cli_args = self.run_cmd(input)
        
        #Track that we have all the expected cli args
        unused_cli_args = {}
        for expected_cli_arg in expected_cli_args.keys():
            unused_cli_args[expected_cli_arg] = True
        
        #go through what we got
        value_to_check = None
        for cli_arg in cli_args:
            if value_to_check is not None:
                self.assertEquals(str(cli_arg), str(value_to_check))
                value_to_check = None
            else:
                assert(cli_arg in expected_cli_args)
                unused_cli_args.pop(cli_arg, None)
                value_to_check = expected_cli_args[cli_arg]
        
        #make sure nothing is left
        assert (not unused_cli_args), "Expected additional CLI options: {0}".format(str(unused_cli_args))

#
# Tool plugin classes
#

class ToolCanRunUnitTest(ExecUnitTest):
    """
    Class for writing tool plug-in can-run unit tests
    """
    progname = "can-run"
    result_valid_field = "can-run"
    error_field = "reasons"
    has_single_error = False

class ToolDurationUnitTest(ExecUnitTest):
    """
    Class for writing tool plug-in duration unit tests
    """
    progname = "duration"
    
    def assert_duration(self, input, expected_duration):
        """
        Run duration and verify value is what is expected
        
        Args:
            input: JSON string of test-spec
            expected_duration: A string with the expected ISO8601 duration returned
        """
        #run command
        result_json = self.run_cmd(input)

        #check duration
        assert ('duration' in result_json)
        self.assertEquals(result_json['duration'], expected_duration)
        
class ToolEnumerateUnitTest(ExecUnitTest):
    """
    Class for writing tool enumerate unit tests. Need to override name, tests and 
    preference
    """
    progname = "enumerate"
    result_valid_field = "valid"
    tests = None #override this
    preference = None #override this

    def test_enumerate_fields(self):
        """
        Run enumerate command, verify is valid JSON, output contain required fields and
        the JSON "name" and "scheduling-class" fields match this classes properties
        """
        #Run command
        result_json = self.run_cmd("")

        #validate JSON returned
        data_validator ={
            "type": "object",
            "properties": {
                "enum": { "$ref": "#/pScheduler/PluginEnumeration/Tool" }
            },
            "additionalProperties": False,
            "required": ["enum"]
        }
        valid, error = json_validate({"enum": result_json}, data_validator)
        assert valid, error
        #verify name is as expected
        self.assertEqual(result_json['name'], self.name)
        #verify tests is as expected
        self.assertEqual(result_json['tests'], self.tests)
        #verify preference is as expected
        self.assertEqual(result_json['preference'], self.preference)

class ToolMergedResultsUnitTest(ExecUnitTest):
    """
    Class for writing tool merged-results unit tests
    """
    progname = "merged-results"
    
    def assert_result_at_index(self, results, expected_result_index, test_spec={}):
        """
        Given list of results, check if returned JSON matches the returned result
        
        Args:
            results: array of results objects
            expected_result_index: int indicating which of provide results is expected
            test_spec: optional. a test_spec object. 
        """
        #run command
        input = json.dumps({"test":{"spec": test_spec}, "results": results})
        result_json = self.run_cmd(input)

        #check results
        self.assertEquals(result_json, results[expected_result_index])

class ToolParticipantDataUnitTest(ExecUnitTest):
    """
    Class for writing tool plug-in participant-data unit tests
    """
    progname = "participant-data"
    
    def assert_participant_data(self, participant, expected_data, test_spec={}):
        """
        Given list of participant, check if returned JSON matches expected data
        
        Args:
            participant: int indicating participant number
            expected_data: object with expected data
            test_spec: optional. a test_spec object. 
        """
        #doesn't really do much so simple test to make sure it runs and returns empt object
        input = json.dumps({"participant": participant, "test": {"spec":test_spec}})
        self.assertEquals(self.run_cmd(input), expected_data)

