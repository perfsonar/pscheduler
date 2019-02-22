#
# Validator for "http" Test
#

# TODO: _ for sensitive values

from pscheduler import json_validate

def spec_is_valid(json):

    schema = {
        "type": "object",
        "properties": {
            "schema":       { "$ref": "#/pScheduler/Cardinal" },
            "host":         { "$ref": "#/pScheduler/Host" },
            "host-node":    { "$ref": "#/pScheduler/Host" },
            "url":          { "$ref": "#/pScheduler/URL" },
            "parse":        { "$ref": "#/pScheduler/String" },
            "timeout":      { "$ref": "#/pScheduler/Duration" },
        },
        "required": [ "url" ],
        "additionalProperties": False
    }

    return json_validate(json, schema)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":  { "$ref": "#/pScheduler/Boolean" },
            "time":       { "$ref": "#/pScheduler/Duration" },
        },
        "required": [
            "schema",
            "succeeded",
            "time",
            ],
        "additionalProperties": True
    }
    return json_validate(json, schema)

def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "url":          { "$ref": "#/pScheduler/Limit/String" },
            "host":            { "$ref": "#/pScheduler/Limit/String" },
            "host-node":     { "$ref": "#/pScheduler/Limit/String" },
            "timeout":         { "$ref": "#/pScheduler/Limit/Duration" },
            "parse":           { "$ref": "#/pScheduler/Limit/String" },
        },
        "additionalProperties": False
    }

    return json_validate(json, schema)
