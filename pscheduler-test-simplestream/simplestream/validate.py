#
# Validator for "simplestream" Test
#

from pscheduler import json_validate

def spec_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "dawdle":         { "$ref": "#/pScheduler/Duration" },
            "fail":           { "$ref": "#/pScheduler/Probability" },
            "dest":           { "$ref": "#/pScheduler/Host" },
            "schema":         { "$ref": "#/pScheduler/Cardinal" },
            "source":         { "$ref": "#/pScheduler/Host" },
            "test-material":  { "$ref": "#/pScheduler/String" },
            "timeout":        { "$ref": "#/pScheduler/Duration" },
            },
        "required": [
            "dest",
            "schema",
            ]
        }
    return json_validate(json, schema)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "dawdled":       { "$ref": "#/pScheduler/Duration" },
            "elapsed-time":  { "$ref": "#/pScheduler/Duration" },
            "received":      { "$ref": "#/pScheduler/String" },
            "schema":        { "$ref": "#/pScheduler/Cardinal" },
            "sent":          { "$ref": "#/pScheduler/String" },
            "succeeded":     { "$ref": "#/pScheduler/Boolean" },
            },
        "required": [
            "dawdled",
            "elapsed-time",
            "received",
            "schema",
            "sent",
            "succeeded",
            ]
        }
    return json_validate(json, schema)


def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "dawdle":        { "$ref": "#/pScheduler/Limit/Duration" },
            "fail":          { "$ref": "#/pScheduler/Limit/Probability" },
            "dest":          { "$ref": "#/pScheduler/Limit/String" },
            "test-material": { "$ref": "#/pScheduler/Limit/String" },
            "timeout":       { "$ref": "#/pScheduler/Limit/Duration" }
        },
        "additionalProperties": False
        }

    return json_validate(json, schema)
