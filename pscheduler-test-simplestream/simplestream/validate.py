#
# Validator for "simplestream" Test
#

from pscheduler import json_validate, json_check_schema

MAX_SCHEMA = 2

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
            }
        }
    }

    try:
        json_check_schema(json, MAX_SCHEMA)
    except ValueError as ex:
        return (False, str(ex))

    schema = json.get("schema", 1)        

    # Build a temporary structure with a reference that points
    # directly at the validator for the specified version of the
    # schema.  Using oneOf or anyOf results in error messages that are
    # difficult to decipher.

    temp_schema = {
        "local": SPEC_SCHEMA["local"],
        "$ref":"#/local/v%d" % schema
    }

    return json_validate(json, temp_schema)



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
            "ip-version":    { "$ref": "#/pScheduler/Limit/IPVersion" },
            "test-material": { "$ref": "#/pScheduler/Limit/String" },
            "timeout":       { "$ref": "#/pScheduler/Limit/Duration" }
        },
        "additionalProperties": False
    }

    return json_validate(json, schema)
