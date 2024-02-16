#
# Validator for "trace" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate, json_validate_from_standard_template

MAX_SCHEMA = 2

def spec_is_valid(json):
    schema = {
        "versions": {
            "1": {
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
            },
            "2": {
                "type": "object",
                "properties": {
                    "schema":            { "$ref": "#/pScheduler/Cardinal" },
                    "dest":              { "$ref": "#/pScheduler/URLHostPort" },
                    "source":            { "$ref": "#/pScheduler/URLHostPort" },
                    "source-node":       { "$ref": "#/pScheduler/URLHostPort" },
                    "timeout":           { "$ref": "#/pScheduler/Duration" },
                },
                "required": [
                    "dest",
                ]
            }
        }
    }
    return json_validate_from_standard_template(json, schema)


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
