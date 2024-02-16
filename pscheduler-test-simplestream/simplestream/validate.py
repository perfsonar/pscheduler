#
# Validator for "simplestream" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate

MAX_SCHEMA = 3

def spec_is_valid(json):
    SPEC_SCHEMA = {

        "local": {
            "v1" : {
                "type": "object",
                "properties": {
                    "schema":         {" type": "integer", "enum": [ 1 ] },
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
            },
            "v2" : {
                "type": "object",
                "properties": {
                    "schema":         {" type": "integer", "enum": [ 2 ] },
                    "dawdle":         { "$ref": "#/pScheduler/Duration" },
                    "fail":           { "$ref": "#/pScheduler/Probability" },
                    "ip-version":     { "$ref": "#/pScheduler/ip-version" },
                    "dest":           { "$ref": "#/pScheduler/Host" },
                    "dest-node":      { "$ref": "#/pScheduler/URLHostPort" },
                    "source":         { "$ref": "#/pScheduler/Host" },
                    "source-node":    { "$ref": "#/pScheduler/URLHostPort" },
                    "test-material":  { "$ref": "#/pScheduler/String" },
                    "timeout":        { "$ref": "#/pScheduler/Duration" },
                },
                "required": [
                    "schema", "dest"
                ]
            },
            "v3" : {
                "type": "object",
                "properties": {
                    "schema":         {" type": "integer", "enum": [ 3 ] },
                    "dawdle":         { "$ref": "#/pScheduler/Duration" },
                    "fail":           { "$ref": "#/pScheduler/Probability" },
                    "ip-version":     { "$ref": "#/pScheduler/ip-version" },
                    "dest":           { "$ref": "#/pScheduler/Host" },
                    "dest-node":      { "$ref": "#/pScheduler/URLHostPort" },
                    "port":           { "$ref": "#/pScheduler/IPPort" },
                    "source":         { "$ref": "#/pScheduler/Host" },
                    "source-node":    { "$ref": "#/pScheduler/URLHostPort" },
                    "test-material":  { "$ref": "#/pScheduler/String" },
                    "timeout":        { "$ref": "#/pScheduler/Duration" },
                },
                "required": [
                    "schema", "dest"
                ]
            },
        }
    }

    # Build a temporary structure with a reference that points
    # directly at the validator for the specified version of the
    # schema.  Using oneOf or anyOf results in error messages that are
    # difficult to decipher.

    temp_schema = {
        "local": SPEC_SCHEMA["local"],
        "$ref":"#/local/v%s" % json.get("schema", 1)
    }

    return json_validate(json, temp_schema, max_schema=MAX_SCHEMA)



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
            "error":         { "$ref": "#/pScheduler/String" },
            "diags":         { "$ref": "#/pScheduler/String" }
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
