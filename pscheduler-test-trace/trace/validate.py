#
# Validator for "trace" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate

MAX_SCHEMA = 2

SPEC_SCHEMA = {
    "local": {

        "algorithm": {
            "type": "string"
        },

        "probe-type": {
            "type": "string",
            "enum": ["icmp", "udp", "tcp"]
        },

        "v1" : {
            "type": "object",
            "properties": {
                "schema":      { "type": "integer", "enum": [ 1 ] },
                "algorithm":   { "$ref": "#/pScheduler/String" },
                "as":          { "$ref": "#/pScheduler/Boolean" },
                "dest-port":   { "$ref": "#/pScheduler/IPPort" },
                "dest":        { "$ref": "#/pScheduler/Host" },
                "first-ttl":   { "$ref": "#/pScheduler/Cardinal" },
                "fragment":    { "$ref": "#/pScheduler/Boolean" },
                "hops":        { "$ref": "#/pScheduler/Cardinal" },
                "hostnames":   { "$ref": "#/pScheduler/Boolean" },
                "ip-tos":      { "$ref": "#/pScheduler/Cardinal" },
                "ip-version":  { "$ref": "#/pScheduler/ip-version" },
                "length":      { "$ref": "#/pScheduler/Cardinal" },
                "probe-type":  { "$ref": "#/local/probe-type" },
                "queries":     { "$ref": "#/pScheduler/Cardinal" },
                "sendwait":    { "$ref": "#/pScheduler/Duration" },
                "source":      { "$ref": "#/pScheduler/Host" },
                "source-node": { "$ref": "#/pScheduler/URLHostPort" },
                "wait":        { "$ref": "#/pScheduler/Duration" }
            },
            "required": [
                "dest"
            ]
        },

        "v2" : {
            "type": "object",
            "properties": {
                "schema":      { "type": "integer", "enum": [ 2 ] },
                "algorithm":   { "$ref": "#/pScheduler/String" },
                "as":          { "$ref": "#/pScheduler/Boolean" },
                "dest-port":   { "$ref": "#/pScheduler/IPPort" },
                "dest":        { "$ref": "#/pScheduler/Host" },
                "first-ttl":   { "$ref": "#/pScheduler/Cardinal" },
                "flow-label":  { "$ref": "#/pScheduler/Cardinal" },
                "fragment":    { "$ref": "#/pScheduler/Boolean" },
                "hops":        { "$ref": "#/pScheduler/Cardinal" },
                "hostnames":   { "$ref": "#/pScheduler/Boolean" },
                "ip-tos":      { "$ref": "#/pScheduler/Cardinal" },
                "ip-version":  { "$ref": "#/pScheduler/ip-version" },
                "length":      { "$ref": "#/pScheduler/Cardinal" },
                "probe-type":  { "$ref": "#/local/probe-type" },
                "queries":     { "$ref": "#/pScheduler/Cardinal" },
                "sendwait":    { "$ref": "#/pScheduler/Duration" },
                "source":      { "$ref": "#/pScheduler/Host" },
                "source-node": { "$ref": "#/pScheduler/URLHostPort" },
                "wait":        { "$ref": "#/pScheduler/Duration" }
            },
            "required": [
                "dest"
            ]
        }
    }
}



def spec_is_valid(input_json):

    # Build a temporary structure with a reference that points
    # directly at the validator for the specified version of the
    # schema.  Using oneOf or anyOf results in error messages that are
    # difficult to decipher.

    temp_schema = {
        "local": SPEC_SCHEMA["local"],
        "$ref":"#/local/v%s" % input_json.get("schema", 1)
    }

    return json_validate(input_json, temp_schema, max_schema=MAX_SCHEMA)



def result_is_valid(json):
    schema = {
        "local": {
            "hop": {
                "type": "object",
                "properties": {
                    "ip": { "$ref": "#/pScheduler/IPAddress" },
                    "hostname": { "$ref": "#/pScheduler/Host" },
                    "rtt": { "$ref": "#/pScheduler/Duration" },
                    "as": { "$ref": "#/pScheduler/AS" },
                    "error": { "$ref": "#/pScheduler/icmp-error" },
                    "mtu":     { "$ref": "#/pScheduler/Cardinal" }
                    },
                "required": [
                    # Nothing required.
                    ]
                },

            "hoparray": {
                "type": "array",
                "items": { "$ref": "#/local/hop" }
            }
        },

        "type": "object",
        "properties": {
            "schema": { "$ref": "#/pScheduler/Cardinal" },
            "paths": {
                "type": "array",
                "items": { "$ref": "#/local/hoparray" },
                },
            "succeeded": { "$ref": "#/pScheduler/Boolean" },
            "error": { "$ref": "#/pScheduler/String" },
            "diags": { "$ref": "#/pScheduler/String" }
            },
        "required": [
            "paths",
            "succeeded",
            ]
        }
    return json_validate(json, schema)
