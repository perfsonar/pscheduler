#
# Validator for "s3throughput" Test
#

#
# Development Order #3:
#
# This file determines the required and optional data types which are 
# allowed to be in the test spec, result, and limit. This is used
# for validation of these structures.
#
# Several existing datatypes are available for use at:
# pscheduler/python-pscheduler/pscheduler/pscheduler/jsonval.py
# 

from pscheduler import json_validate
MAX_SCHEMA = 1

def spec_is_valid(json):

    schema = {
        "local": {
            # Local data types such as this can be defined within this file,
            # but are not necessary
            },
        "Spec": {
            "type": "object",
            # schema, host, host-node, and timeout are standard,
            # and should be included
            "properties": {
                "schema":       { "$ref": "#/pScheduler/Cardinal" },
                "host":         { "$ref": "#/pScheduler/Host" },
                "host-node":    { "$ref": "#/pScheduler/Host" },
                "duration":     { "$ref": "#/pScheduler/Duration" },
                "timeout":      { "$ref": "#/pScheduler/Duration" },
		"access-key":   { "$ref": "#/pScheduler/String" },
	        "bucket":       { "$ref": "#/pScheduler/String" },
             	"secret-key":   { "$ref": "#/pScheduler/String" },
	        "url":	        { "$ref": "#/pScheduler/String" },
		"iterations":   { "$ref": "#/pScheduler/Cardinal" },
		"object-size":  { "$ref": "#/pScheduler/String" }
            },
            # If listed here, data of this type MUST be in the test spec
            "required": [
                "access-key",
		"bucket",
		"secret-key",
                "url"
            ],
        },
        # Set to false if ONLY required options should be used
        "additionalProperties": True
    }

    return json_validate(json, schema, max_schema=MAX_SCHEMA)

def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":  { "$ref": "#/pScheduler/Boolean" },
	    "loops":       { "$ref": "#/pScheduler/String" },
	    "average_put_time": { "$ref": "#/pScheduler/Float" },
	    "average_get_time": { "$ref": "#/pScheduler/Float" },
	    "average_delete_time": { "$ref": "#/pScheduler/Float" },
            "time" : { "$ref": "#/pScheduler/Duration" }    
	},
        "required": [
            "schema",
            "succeeded",
	    "average_put_time",
	    "average_get_time",
	    "average_delete_time"
            ]
        }
    return json_validate(json, schema)

def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "host":            { "$ref": "#/pScheduler/Limit/String" },
            "host-node":       { "$ref": "#/pScheduler/Limit/String" },
            "testtype":        { "$ref": "#/local/Type" },
            "timeout":         { "$ref": "#/pScheduler/Limit/Duration" },
        },
        "additionalProperties": False
        }

    return json_validate(json, schema)
