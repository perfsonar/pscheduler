#
# Validator for "simplestream" Test
#

from pscheduler import json_validate

def spec_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":         { "$ref": "#/pScheduler/Cardinal" },
            "dawdle":         { "$ref": "#/pScheduler/Duration" },
            "fail":           { "$ref": "#/pScheduler/Probability" },
            "dest":           { "$ref": "#/pScheduler/Host" },
            "dest-node":      { "$ref": "#/pScheduler/URLHostPort" },
            "source":         { "$ref": "#/pScheduler/Host" },
            "source-node":    { "$ref": "#/pScheduler/URLHostPort" },
            "test-material":  { "$ref": "#/pScheduler/String" },
            "timeout":        { "$ref": "#/pScheduler/Duration" },
            },
        "required": [
            "dest"
            ]
        }
    return json_validate(json, schema)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":         { "$ref": "#/pScheduler/Cardinal" },
            "dawdled":       { "$ref": "#/pScheduler/Duration" },
            "elapsed-time":  { "$ref": "#/pScheduler/Duration" },
            "received":      { "$ref": "#/pScheduler/String" },
            "sent":          { "$ref": "#/pScheduler/String" },
            "succeeded":     { "$ref": "#/pScheduler/Boolean" },
            },
        "required": [
            "dawdled",
            "elapsed-time",
            "received",
            "sent",
            "succeeded",
            ]
        }
    return json_validate(json, schema)


def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
        "schema": { "$ref": "#/pScheduler/Cardinal" },
            "dawdle":        { "$ref": "#/pScheduler/Limit/Duration" },
            "fail":          { "$ref": "#/pScheduler/Limit/Probability" },
            "dest":          { "$ref": "#/pScheduler/Limit/String" },
            "test-material": { "$ref": "#/pScheduler/Limit/String" },
            "timeout":       { "$ref": "#/pScheduler/Limit/Duration" }
        },
        "additionalProperties": False
        }

    return json_validate(json, schema)
