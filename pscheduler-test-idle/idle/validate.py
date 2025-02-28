# change max schema to 2
# Validator for "idle" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_standard_template_max_schema
from pscheduler import json_validate_from_standard_template


SPEC_SCHEMA = {
    "local": { },

    "versions": {

        "1": {
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

        "2": {
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

def spec_max_schema():
    return json_standard_template_max_schema(SPEC_SCHEMA)

def spec_is_valid(json):
    return json_validate_from_standard_template(json, SPEC_SCHEMA)


RESULT_SCHEMA = {

    "local": {},

    "versions": {

        "1": {
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
    }
}


def result_max_schema():
    return json_standard_template_max_schema(RESULT_SCHEMA)

def result_is_valid(json):
    return json_validate_from_standard_template(json, RESULT_SCHEMA)
