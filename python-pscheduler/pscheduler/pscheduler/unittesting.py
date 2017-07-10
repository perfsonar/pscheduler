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
from pscheduler import run_program, json_validate
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

