#
# Validator for "psresponse" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

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
        "$ref":"#/local/v%s" % json.get("schema", 1)
    }

    return json_validate(json, temp_schema, max_schema=MAX_SCHEMA)



RESULT_SCHEMA = {
    "local": {

        "v1" : {
            "type": "object",
            "properties": {
                "schema":     { "type": "integer", "enum": [ 1 ] },
                "succeeded":  { "$ref": "#/pScheduler/Boolean" },
                "reason":      { "$ref": "#/pScheduler/String" },
                "time":      {"anyOf": [
                                 { "type": "null" },
                                 { "$ref": "#/pScheduler/Duration" }
                              ]} 
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
        "$ref":"#/local/v%s" % json.get("schema", 1)
    }

    return json_validate(json, temp_schema, max_schema=MAX_SCHEMA)
