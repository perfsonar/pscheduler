#
# Validator for "idlebg" Test
#

from pscheduler import json_validate

def spec_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "duration":         { "$ref": "#/pScheduler/Duration" },
            "host":             { "$ref": "#/pScheduler/Host" },
            "interval":         { "$ref": "#/pScheduler/Duration" },
            "parting-comment":  { "$ref": "#/pScheduler/String" },
            "schema":           { "$ref": "#/pScheduler/Cardinal" },
            "starting-comment": { "$ref": "#/pScheduler/String" },
            },
        "required": [
            "duration",
            "schema",
            ]
        }
    return json_validate(json, schema)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":           { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":        { "$ref": "#/pScheduler/Boolean" },
            "time-slept":         { "$ref": "#/pScheduler/Duration" },
            },
        "required": [
            "schema",
            "succeeded",
            "time-slept",
            ]
        }
    return json_validate(json, schema)


def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "duration":         { "$ref": "#/pScheduler/Limit/Duration" },
            "starting-comment": { "$ref": "#/pScheduler/Limit/String" },
            "parting-comment":  { "$ref": "#/pScheduler/Limit/String" }
        },
        "additionalProperties": False
        }

    return json_validate(json, schema)
