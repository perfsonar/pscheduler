# change max schema to 2
# Validator for "idle" Test
#

from pscheduler import json_validate

MAX_SCHEMA = 2


def spec_is_valid(json):
    schema = {
        "local": {
            "v1": {
                "type": "object",
                "properties": {
                    "schema":           { "type": "integer", "enum": [ 1 ] },
                    "duration":         { "$ref": "#/pScheduler/Duration" },
                    "host":             { "$ref": "#/pScheduler/Host" },
                    "host-node":        { "$ref": "#/pScheduler/URLHostPort" },
                    "parting-comment":  { "$ref": "#/pScheduler/String" },
                    "starting-comment": { "$ref": "#/pScheduler/String" },
                },
                "additionalProperties": False,
                "required": [
                    "duration",
                ]
            },
            "v2": {
                "type": "object",
                "properties": {
                    "schema":           { "type": "integer", "enum": [ 2 ] },
                    "duration":         { "$ref": "#/pScheduler/Duration" },
                    "host":             { "type": "array",
                                          "items": { "$ref": "#/pScheduler/Host" },
                                          "minItems" : 1 },
                    "parting-comment":  { "$ref": "#/pScheduler/String" },
                    "starting-comment": { "$ref": "#/pScheduler/String" },
                },
                "additionalProperties": False,
                "required": [
                    "duration",
                ]
            }
        }
    }

    # Build a temporary structure with a reference that points
    # directly at the validator for the specified version of the
    # schema.  Using oneOf or anyOf results in error messages that are
    # difficult to decipher.
    temp_schema = {
        "local": schema["local"],
        "$ref":"#/local/v%d" % json.get("schema", 1)
    }

    return json_validate(json, temp_schema, max_schema=MAX_SCHEMA)

def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":           { "$ref": "#/pScheduler/Cardinal" },
            "duration":         { "$ref": "#/pScheduler/Duration" },
            "succeeded":        { "$ref": "#/pScheduler/Boolean" },
            "error":            { "$ref": "#/pScheduler/String" },
            "diags":            { "$ref": "#/pScheduler/String" }
            },
        "additionalProperties": False,
        "required": [
            "duration",
            "succeeded",
            ]
        }
    return json_validate(json, schema)


def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":           { "$ref": "#/pScheduler/Cardinal" },
            "duration":         { "$ref": "#/pScheduler/Limit/Duration" },
            "starting-comment": { "$ref": "#/pScheduler/Limit/String" },
            "parting-comment":  { "$ref": "#/pScheduler/Limit/String" }
        },
        "additionalProperties": False
        }

    return json_validate(json, schema)
