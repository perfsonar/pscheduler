#
# Validator for "s3throughput" Test
#

from pscheduler import json_validate_from_standard_template
from pscheduler import json_standard_template_max_schema


#
# Test Specification
#

# NOTE: A large dictionary of existing, commonly-used datatypes used
# throughout pScheduler is defined in
# pscheduler/python-pscheduler/pscheduler/pscheduler/jsonval.py.
# Please use those where possible.

SPEC_SCHEMA = {
    
    "local": {
        # Define any local types used in the spec here
    },
    
    "versions": {
        
        # Initial version of the specification
        "1": {
            "type": "object",
            "properties": {
                "schema": { "type": "integer", "enum": [ 1 ] },
                "host":        { "$ref": "#/pScheduler/Host" },
                "host-node":   { "$ref": "#/pScheduler/Host" },
                "duration":    { "$ref": "#/pScheduler/Duration" },
                "timeout":     { "$ref": "#/pScheduler/Duration" },
	        "_access-key": { "$ref": "#/pScheduler/String" },
	        "bucket":      { "$ref": "#/pScheduler/String" },
                "_secret-key": { "$ref": "#/pScheduler/String" },
	        "url":	       { "$ref": "#/pScheduler/URL" },
       	        "iterations":  { "$ref": "#/pScheduler/Cardinal" },
	        "object-size": { "$ref": "#/pScheduler/Cardinal" }
            },
            # If listed here, data of this type MUST be in the test spec
            "required": [
                "_access-key",
                "bucket",
	        "_secret-key",
                "url",
                "object-size"
            ],
            # Set to false if ONLY required options should be used
            "additionalProperties": False
        },
        
        # Second and later versions of the specification
        # "2": {
        #    "type": "object",
        #    "properties": {
        #        "schema": { "type": "integer", "enum": [ 2 ] },
        #        ...
        #    },
        #    "required": [
        #        "schema",
        #        ...
        #    ],
        #    "additionalProperties": False
        #},
        
    }
}


def spec_max_schema():
    return json_standard_template_max_schema(SPEC_SCHEMA)


def spec_is_valid(json):
    return json_validate_from_standard_template(json, SPEC_SCHEMA)



#
# Test Result
#

RESULT_SCHEMA = {

    "local": {
        # Define any local types here.
    },

    "versions": {

        "1": {
            "type": "object",
            "properties": {
                "schema":              { "type": "integer", "enum": [ 1 ] },
                "succeeded":           { "$ref": "#/pScheduler/Boolean" },
	        "error":               { "$ref": "#/pScheduler/String" },
	        "diags":               { "$ref": "#/pScheduler/String" },
	        "loops":               { "$ref": "#/pScheduler/String" },
	        "average_put_time":    { "$ref": "#/pScheduler/Float" },
	        "average_get_time":    { "$ref": "#/pScheduler/Float" },
	        "average_delete_time": { "$ref": "#/pScheduler/Float" },
                "time" :               { "$ref": "#/pScheduler/Duration" }    
	    },
            "required": [
                "succeeded",
	        "average_put_time",
	        "average_get_time",
	        "average_delete_time"
            ]
        }
    }
}


def result_max_schema():
    return json_standard_template_max_schema(RESULT_SCHEMA)


def result_is_valid(json):
    return json_validate_from_standard_template(json, RESULT_SCHEMA)
