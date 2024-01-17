#
# Validator for a pScheduler Test
#

#
# Development Order #3:
#
# This file determines the required and optional data types which are 
# allowed to be in the test spec and result. This is used
# for validation of these structures.
#
# Several existing datatypes are available for use at:
# pscheduler/python-pscheduler/pscheduler/pscheduler/jsonval.py
# 

from pscheduler import json_validate

MAX_SCHEMA = 2

def spec_is_valid(json):

    SPEC_SCHEMA = {

        "local": {
            "v1": {
                "type": "object",
                "properties": {
                    "schema":       { "$ref": "#/pScheduler/Cardinal" },
                    "source":       { "$ref": "#/pScheduler/Host" },
                    "source-node":  { "$ref": "#/pScheduler/Host" },
                    "dest":         { "$ref": "#/pScheduler/Host" },
                    "port":         { "$ref": "#/pScheduler/IPPort" },
                },
                "required": [
                    "dest",
                ],
                "additionalProperties": False
            },
            "v2": {
                "type": "object",
                "properties": {
                    "schema":       { "$ref": "#/pScheduler/Cardinal" },
                    "source":       { "$ref": "#/pScheduler/Host" },
                    "source-node":  { "$ref": "#/pScheduler/Host" },
                    "dest":         { "$ref": "#/pScheduler/Host" },
                    "ip-version":   { "$ref": "#/pScheduler/ip-version" },
                    "port":         { "$ref": "#/pScheduler/IPPort" },
                },
                "required": [
                    "dest",
                ],
                "additionalProperties": False
            }
        }
    }

    # Build a temporary structure with a reference that points
    # directly at the validator for the specified version of the
    # schema.  Using oneOf or anyOf results in error messages that are
    # difficult to decipher.

    temp_schema = {
        "local": SPEC_SCHEMA["local"],
        "$ref":"#/local/v%s" % json.get("schema", 1)
    }

    return json_validate(json, temp_schema, max_schema=MAX_SCHEMA)


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
