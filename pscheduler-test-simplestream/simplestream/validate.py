#
# Validator for "simplestream" Test
#

from pscheduler import json_validate

def spec_is_valid(json):
    schema = {

        "local": {
            "SimplestreamTestSpecification_V1" : {
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
            "SimplestreamTestSpecification_V2" : {
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

            "SimplestreamTestSpecification": {
                "anyOf": [
                    { "$ref": "#/local/SimplestreamTestSpecification_V1" },
                    { "$ref": "#/local/SimplestreamTestSpecification_V2" }
                ]
            }

        },

        "$ref": "#/local/SimplestreamTestSpecification"
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
            "ip-version":    { "$ref": "#/pScheduler/Limit/IPVersion" },
            "test-material": { "$ref": "#/pScheduler/Limit/String" },
            "timeout":       { "$ref": "#/pScheduler/Limit/Duration" }
        },
        "additionalProperties": False
    }

    return json_validate(json, schema)
