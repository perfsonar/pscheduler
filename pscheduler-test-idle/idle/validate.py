#
# Validator for "idle" Test
#

from pscheduler import json_validate

def spec_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":           { "$ref": "#/pScheduler/Cardinal" },
            "duration":         { "$ref": "#/pScheduler/Duration" },
            "host":             { "$ref": "#/pScheduler/Host" },
            "parting-comment":  { "$ref": "#/pScheduler/String" },
            "starting-comment": { "$ref": "#/pScheduler/String" },
            },
        "additionalProperties": False,
        "required": [
            "duration",
            ]
        }
    return json_validate(json, schema)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":           { "$ref": "#/pScheduler/Cardinal" },
            "duration":         { "$ref": "#/pScheduler/Duration" },
            "succeeded":        { "$ref": "#/pScheduler/Boolean" },
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
