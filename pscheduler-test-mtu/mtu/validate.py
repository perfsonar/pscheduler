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
        "type": "object",
        # schema, host, host-node, and timeout are standard,
        # and should be included
        "properties": {
            "schema":       { "$ref": "#/pScheduler/Cardinal" },
            "source":       { "$ref": "#/pScheduler/Host" },
            "source-node":  { "$ref": "#/pScheduler/Host" },
            "dest":         { "$ref": "#/pScheduler/Host" },
        },
        # If listed here, data of this type MUST be in the test spec
        "required": [
            "dest",
            ],
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
            "mtu":        { "$ref": "#/pScheduler/Cardinal" },
            },
        "required": [
            "succeeded",
            "mtu",
            ]
        }
    return json_validate(json, schema)

