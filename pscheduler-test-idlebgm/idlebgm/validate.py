#
# Validator for "idlebg" Test
#

from pscheduler import json_validate

MAX_SCHEMA = 1

def spec_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":           { "$ref": "#/pScheduler/Cardinal" },
            "duration":         { "$ref": "#/pScheduler/Duration" },
            "host":             { "$ref": "#/pScheduler/Host" },
            "host-node":        { "$ref": "#/pScheduler/URLHostPort" },
            "interval":         { "$ref": "#/pScheduler/Duration" },
            "parting-comment":  { "$ref": "#/pScheduler/String" },
            "starting-comment": { "$ref": "#/pScheduler/String" },
            },
        "required": [
            "duration"
            ]
        }

    return json_validate(json, schema, max_schema=MAX_SCHEMA)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":           { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":        { "$ref": "#/pScheduler/Boolean" },
            "error":            { "$ref": "#/pScheduler/String" },
            "diags":            { "$ref": "#/pScheduler/String" },
            "time-slept":         { "$ref": "#/pScheduler/Duration" },
            },
        "required": [
            "succeeded",
            "time-slept",
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
