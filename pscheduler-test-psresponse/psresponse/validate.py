#
# Validator for "psresponse" Test
#

from pscheduler import json_validate

MAX_SCHEMA = 1

SPEC_SCHEMA = {
    "local": {

        "v1" : {
            "type": "object",
            "properties": {
                "schema":      { "type": "integer", "enum": [ 1 ] },
                "source":         { "$ref": "#/pScheduler/Host" },
                "source-node":    { "$ref": "#/pScheduler/Host" },
                "dest":          { "$ref": "#/pScheduler/Host" },
                "timeout":      { "$ref": "#/pScheduler/Duration" }
            },
            "required": [ "dest" ],
            "additionalProperties": False
        }

    }
}


def spec_is_valid(json):

    # Build a temporary structure with a reference that points
    # directly at the validator for the specified version of the
    # schema.  Using oneOf or anyOf results in error messages that are
    # difficult to decipher.

    temp_schema = {
        "local": SPEC_SCHEMA["local"],
        "$ref":"#/local/v%d" % json.get("schema", 1)
    }

    return json_validate(json, temp_schema, max_schema=MAX_SCHEMA)



RESULT_SCHEMA = {
    "local": {

        "v1" : {
            "type": "object",
            "properties": {
                "schema":     { "type": "integer", "enum": [ 1 ] },
                "succeeded":  { "$ref": "#/pScheduler/Boolean" },
                "error":      { "$ref": "#/pScheduler/String" },
                "diags":      { "$ref": "#/pScheduler/String" },
                "time":       { "$ref": "#/pScheduler/Duration" }
            },
            "required": [
                "succeeded",
                "time",
            ],
            "additionalProperties": False
        }

    }
}


def result_is_valid(json):

    # Build a temporary structure with a reference that points
    # directly at the validator for the specified version of the
    # schema.  Using oneOf or anyOf results in error messages that are
    # difficult to decipher.

    temp_schema = {
        "local": RESULT_SCHEMA["local"],
        "$ref":"#/local/v%d" % json.get("schema", 1)
    }

    return json_validate(json, temp_schema, max_schema=MAX_SCHEMA)



def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "url":          { "$ref": "#/pScheduler/Limit/String" },
            "host":            { "$ref": "#/pScheduler/Limit/String" },
            "host-node":     { "$ref": "#/pScheduler/Limit/String" },
            "timeout":         { "$ref": "#/pScheduler/Limit/Duration" },
            "parse":           { "$ref": "#/pScheduler/Limit/String" },
            "always-succeed":  { "$ref": "#/pScheduler/Boolean" },
        },
        "additionalProperties": False
    }

    return json_validate(json, schema)
