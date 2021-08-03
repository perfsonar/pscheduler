#
# Validator for a pScheduler Test
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
        "local": {},
            # Local data types such as this can be defined within this file,
            # but are not necessary
	"type": "object",
	# schema, host, host-node, and timeout are standard,
	# and should be included
	"properties": {
	    "schema":       { "$ref": "#/pScheduler/Cardinal" },
	    "host":         { "$ref": "#/pScheduler/Host" },
	    "host-node":    { "$ref": "#/pScheduler/Host" },
	    "timeout":      { "$ref": "#/pScheduler/Duration" },
	    "interface":    { "$ref": "#/pScheduler/AnyJSON" },
	},
	# If listed here, data of this type MUST be in the test spec
	"required": [],
    
        # Set to false if ONLY required options should be used
        "additionalProperties": False
    }

    return json_validate(json, schema, max_schema=MAX_SCHEMA)

def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":  { "$ref": "#/pScheduler/Boolean" },
            "time":       { "$ref": "#/pScheduler/Duration" },
	        "ip_address": { "$ref": "#/pScheduler/AnyJSON" },
            },
        "required": [
            "time",
            "ip_address",
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

    return json_validate(json, schema, max_schema=MAX_SCHEMA)
