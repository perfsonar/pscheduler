#
# Validator for "noop" Test
#

from pscheduler import json_validate

MAX_SCHEMA = 1

def spec_is_valid(json):
    schema = {
        "local": {
            "v1": {
                "type": "object",
                "properties": {
                    "schema":           { "type": "integer", "enum": [ 1 ] },
                    "data":             { "$ref": "#/pScheduler/AnyJSON" },
                    "host":             { "$ref": "#/pScheduler/Host" },
                    "host-node":        { "$ref": "#/pScheduler/URLHostPort" }
                },
                "additionalProperties": False,
                "required": [
                    "data",
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
            "data":             { "$ref": "#/pScheduler/AnyJSON" },
            "succeeded":        { "$ref": "#/pScheduler/Boolean" }
            },
        "additionalProperties": False,
        "required": [
            "data",
            "succeeded",
            ]
        }
    return json_validate(json, schema)
