#
# Validator for "trace" Test
#

from pscheduler import json_validate

MAX_SCHEMA = 1

def spec_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":            { "$ref": "#/pScheduler/Cardinal" },
            "dest":              { "$ref": "#/pScheduler/URLHostPort" },
            "source":            { "$ref": "#/pScheduler/URLHostPort" },
            "timeout":           { "$ref": "#/pScheduler/Duration" },
            },
        "required": [
            "dest",
            ]
        }
    return json_validate(json, schema, max_schema=MAX_SCHEMA)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema": { "$ref": "#/pScheduler/Cardinal" },
            "succeeded": { "$ref": "#/pScheduler/Boolean" },
            "error": { "$ref": "#/pScheduler/String" },
            "diags": { "$ref": "#/pScheduler/String" },
            "local": { "$ref": "#/pScheduler/ClockState" },
            "remote": { "$ref": "#/pScheduler/ClockState" },
            "difference": { "$ref": "#/pScheduler/Duration" },
            },
        "required": [
            "succeeded",
            "local",
            "remote",
            "difference",
            ]
        }
    return json_validate(json, schema)


def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema": { "$ref": "#/pScheduler/Cardinal" },
            "dest":              { "$ref": "#/pScheduler/Limit/String" },
            "source":            { "$ref": "#/pScheduler/Limit/String" },
            "source-node":       { "$ref": "#/pScheduler/Limit/String" },
            "timeout":           { "$ref": "#/pScheduler/Limit/Duration" }
        },
        "additionalProperties": False
        }

    return json_validate(json, schema, max_schema=MAX_SCHEMA)
