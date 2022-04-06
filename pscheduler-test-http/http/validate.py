#
# Validator for "http" Test
#

# TODO: _ for sensitive values

from pscheduler import json_validate

MAX_SCHEMA = 4

HEADERS_SCHEMA = {
            "type": "object",
            "patternProperties": {
                # Regex is per https://tools.ietf.org/html/rfc7230#section-3.2
                "^[!#\$%&'*+\-.\^`|~0-9A-Za-z]+$": { "$ref": "#/pScheduler/String" }
            },
            "additionalProperties": False
        }

SPEC_SCHEMA = {
    "local": {

        "headers": HEADERS_SCHEMA,

        "v1" : {
            "type": "object",
            "properties": {
                "schema":      { "type": "integer", "enum": [ 1 ] },
                "host":         { "$ref": "#/pScheduler/Host" },
                "host-node":    { "$ref": "#/pScheduler/Host" },
                "url":          { "$ref": "#/pScheduler/URL" },
                "parse":        { "$ref": "#/pScheduler/String" },
                "timeout":      { "$ref": "#/pScheduler/Duration" }
            },
            "required": [ "url" ],
            "additionalProperties": False
        },

        "v2" : {
            "type": "object",
            "properties": {
                "schema":       { "type": "integer", "enum": [ 2 ] },
                "host":         { "$ref": "#/pScheduler/Host" },
                "host-node":    { "$ref": "#/pScheduler/Host" },
                "url":          { "$ref": "#/pScheduler/URL" },
                "parse":        { "$ref": "#/pScheduler/String" },
                "timeout":      { "$ref": "#/pScheduler/Duration" },
                "always-succeed":  { "$ref": "#/pScheduler/Boolean" },
                "keep-content": { "$ref": "#/pScheduler/CardinalZero" }
            },
            "required": [ "schema", "url" ],
            "additionalProperties": False
        },

        "v3" : {
            "type": "object",
            "properties": {
                "schema":       { "type": "integer", "enum": [ 3 ] },
                "host":         { "$ref": "#/pScheduler/Host" },
                "host-node":    { "$ref": "#/pScheduler/Host" },
                "ip-version":   { "$ref": "#/pScheduler/ip-version" },
                "url":          { "$ref": "#/pScheduler/URL" },
                "parse":        { "$ref": "#/pScheduler/String" },
                "timeout":      { "$ref": "#/pScheduler/Duration" },
                "always-succeed":  { "$ref": "#/pScheduler/Boolean" },
                "keep-content": { "$ref": "#/pScheduler/CardinalZero" }
            },
            "required": [ "schema", "url" ],
            "additionalProperties": False
        },

        "v4" : {
            "type": "object",
            "properties": {
                "schema":       { "type": "integer", "enum": [ 4 ] },
                "host":         { "$ref": "#/pScheduler/Host" },
                "host-node":    { "$ref": "#/pScheduler/Host" },
                "ip-version":   { "$ref": "#/pScheduler/ip-version" },
                "url":          { "$ref": "#/pScheduler/URL" },
                "headers":      { "$ref": "#/local/headers" },
                "parse":        { "$ref": "#/pScheduler/String" },
                "timeout":      { "$ref": "#/pScheduler/Duration" },
                "always-succeed":  { "$ref": "#/pScheduler/Boolean" },
                "keep-content": { "$ref": "#/pScheduler/CardinalZero" }
            },
            "required": [ "schema", "url" ],
            "additionalProperties": False
        }

    }
}


def spec_is_valid(json):

    # Build a temporary structure with a reference that points
    # directly at the validator for the specified version of the
    # schema.  Using oneOf or anyOf results in error messages that are
    # difficult to decipher.

    temp_schema = {
        "local": SPEC_SCHEMA["local"],
        "$ref":"#/local/v%d" % json.get("schema", 1)
    }

    return json_validate(json, temp_schema, max_schema=MAX_SCHEMA)



RESULT_SCHEMA = {
    "local": {

        "headers": HEADERS_SCHEMA,

        "v1" : {
            "type": "object",
            "properties": {
                "schema":     { "type": "integer", "enum": [ 1 ] },
                "succeeded":  { "$ref": "#/pScheduler/Boolean" },
                "error":      { "$ref": "#/pScheduler/String" },
                "diags":      { "$ref": "#/pScheduler/String" },
                "time":       { "$ref": "#/pScheduler/Duration" },
                "found":      { "$ref": "#/pScheduler/Boolean" }
            },
            "required": [
                "succeeded",
                "time",
            ],
            "additionalProperties": False
        },

        "v2" : {
            "type": "object",
            "properties": {
                "schema":     { "type": "integer", "enum": [ 2 ] },
                "succeeded":  { "$ref": "#/pScheduler/Boolean" },
                "error":      { "$ref": "#/pScheduler/String" },
                "diags":      { "$ref": "#/pScheduler/String" },
                "time":       { "$ref": "#/pScheduler/Duration" },
                "found":      { "$ref": "#/pScheduler/Boolean" },
                "status":     { "$ref": "#/pScheduler/Cardinal" },
                "headers":    { "$ref": "#/local/headers" },
                "content":    { "$ref": "#/pScheduler/String" },
            },
            "required": [
                "schema",
                "succeeded",
                "time",
            ],
            "additionalProperties": False
        }

    }
}


def result_is_valid(json):

    # Build a temporary structure with a reference that points
    # directly at the validator for the specified version of the
    # schema.  Using oneOf or anyOf results in error messages that are
    # difficult to decipher.

    temp_schema = {
        "local": RESULT_SCHEMA["local"],
        "$ref":"#/local/v%d" % json.get("schema", 1)
    }

    return json_validate(json, temp_schema, max_schema=MAX_SCHEMA)



def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "url":          { "$ref": "#/pScheduler/Limit/String" },
            "host":            { "$ref": "#/pScheduler/Limit/String" },
            "host-node":     { "$ref": "#/pScheduler/Limit/String" },
            "timeout":         { "$ref": "#/pScheduler/Limit/Duration" },
            "parse":           { "$ref": "#/pScheduler/Limit/String" },
            "always-succeed":  { "$ref": "#/pScheduler/Boolean" },
        },
        "additionalProperties": False
    }

    return json_validate(json, schema)
