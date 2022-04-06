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

    SPEC_SCHEMA = {
        "local": {
            # Local data types such as this can be defined within this file,
            # but are not necessary
            "portlist": {
                "type": "string",
		"pattern" : r'^(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[0-9]{1,4})((,(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[0-9]{1,4}))|(-(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[0-9]{1,4})))*$'
            },
            "HostOrCIDR": {
                "oneOf": [
                     { "$ref": "#/pScheduler/IPCIDR" },
                     { "$ref": "#/pScheduler/Host" }
                ]
            },
            "v1": {
                "type": "object",
                # schema, host, host-node, and timeout are standard,
                # and should be included
                "properties": {
                    "schema":         { "$ref": "#/pScheduler/Cardinal" },
                    "network":        { "$ref": "#/local/HostOrCIDR" },
                    "source":         { "$ref": "#/pScheduler/Host" },
                    "services":       { "$ref": "#/pScheduler/Boolean" },
                    "ports":          { "$ref": "#/local/portlist" },
                    "timeout":        { "$ref": "#/pScheduler/Duration" },
                    "source-node":    { "$ref": "#/pScheduler/URLHostPort"}
                },
                # If listed here, data of this type MUST be in the test spec
                "required": [
                    "network",
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
        "$ref":"#/local/v%d" % json.get("schema", 1)
    }
    return json_validate(json, temp_schema, max_schema=MAX_SCHEMA)

def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":  { "$ref": "#/pScheduler/Boolean" },
            "result":     {
                "succeeded":  { "$ref": "#/pScheduler/Boolean" },
                "result":     { "$ref": "#/pScheduler/AnyJSON" },
                "error":      { "$ref": "#/pScheduler/String" },
                "diags":      { "$ref": "#/pScheduler/String" }
                },
            "error":      { "$ref": "#/pScheduler/String" },
            "diags":      { "$ref": "#/pScheduler/String" }
            },
        "required": [
            "succeeded",
            "result"
            ]
        }
    return json_validate(json, schema)

def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":         { "$ref": "#/pScheduler/Cardinal" },
            "network":        { "$ref": "#/pScheduler/IPCIDR" },
            "source":         { "$ref": "#/pScheduler/IPAddress" },
            "services":       { "$ref": "#/pScheduler/Boolean" },
            "ports":          { "$ref": "#/local/portlist" },
            "timeout":        { "$ref": "#/pScheduler/Duration" },
            "source-node":    { "$ref": "#/pScheduler/URLHostPort"}
        },
        "additionalProperties": False
        }

    return json_validate(json, schema, max_schema=MAX_SCHEMA)
