#
# Validator for "http" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

# TODO: _ for sensitive values

from pscheduler import json_validate



RESULT_SCHEMA = {
    "local": {

        "headers": HEADERS_SCHEMA,

        "v1" : {
            "type": "object",
            "properties": {
                "schema":     { "type": "integer", "enum": [ 1 ] },
                "succeeded":  { "$ref": "#/pScheduler/Boolean" },
                "error":      { "$ref": "#/pScheduler/String" },
                "diags":      { "$ref": "#/pScheduler/String" },
                "time":       { "$ref": "#/pScheduler/Duration" },
                "found":      { "$ref": "#/pScheduler/Boolean" }
            },
            "required": [
                "succeeded",
                "time",
            ],
            "additionalProperties": False
        },

        "v2" : {
            "type": "object",
            "properties": {
                "schema":     { "type": "integer", "enum": [ 2 ] },
                "succeeded":  { "$ref": "#/pScheduler/Boolean" },
                "error":      { "$ref": "#/pScheduler/String" },
                "diags":      { "$ref": "#/pScheduler/String" },
                "time":       { "$ref": "#/pScheduler/Duration" },
                "found":      { "$ref": "#/pScheduler/Boolean" },
                "status":     { "$ref": "#/pScheduler/Cardinal" },
                "headers":    { "$ref": "#/local/headers" },
                "content":    { "$ref": "#/pScheduler/String" },
            },
            "required": [
                "schema",
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
