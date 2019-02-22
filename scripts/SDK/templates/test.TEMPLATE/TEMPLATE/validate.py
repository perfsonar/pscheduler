#
# Validator for "snmpset" Test
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

def spec_is_valid(json):

    schema = {
        "local": {
            # Local data types such as this can be defined within this file,
            # but are not necessary
            "Type": {
                "type": "string",
                "enum": [ "system", "api" ]
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
                    # Here is the datatype we defined on lines 24-27
                    "testtype":     { "$ref": "#/local/Type" },
                },
                # If listed here, data of this type MUST be in the test spec
                "required": [
                    "testtype",
                    ],
            }
        },
        # Set to false if ONLY required options should be used
        "additionalProperties": True
    }

    return json_validate(json, schema)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":  { "$ref": "#/pScheduler/Boolean" },
            "time":       { "$ref": "#/pScheduler/Duration" },
            },
        "required": [
            "schema",
            "succeeded",
            "time",
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
