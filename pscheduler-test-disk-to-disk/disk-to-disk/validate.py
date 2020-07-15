#
# Validator for "disk-to-disk" Test
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
    schema = {"type": "object",
                # schema, host, host-node, and timeout are standard,
                # and should be included
                "properties": {
                    "schema":       { "$ref": "#/pScheduler/Cardinal" },
                    "parallel":     { "$ref": "#/pScheduler/Cardinal" },

                    "host":         { "$ref": "#/pScheduler/Host"     },

                    "dest":         { "$ref": "#/pScheduler/String"   },
                    "source":       { "$ref": "#/pScheduler/String"   },
                    
                    "timeout":      { "$ref": "#/pScheduler/Duration" }, 
                    "min-bandwith": { "$ref": "#/pScheduler/Cardinal" },
                    
                    "max-size":     { "$ref": "#/pScheduler/Cardinal" },
                    "cleanup":      { "$ref": "#/pScheduler/Boolean"  },
                },
                # If listed here, data of this type MUST be in the test spec
                "required":  [
                    "dest", "source"
                    ],

        "additionalProperties": False
    }

    return json_validate(json, schema, max_schema=MAX_SCHEMA)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Cardinal" },
            "time":       { "$ref": "#/pScheduler/Duration" },
            "succeeded":  { "$ref": "#/pScheduler/Boolean"  },
            "bytes-sent": { "$ref": "#/pScheduler/Float" },
            "throughput": { "$ref": "#/pScheduler/Float" },
            },
        "required": [
            "succeeded",
            "time"
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
