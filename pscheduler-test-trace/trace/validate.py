#
# Validator for "trace" Test
#

from pscheduler import json_validate

MAX_SCHEMA = 2

SPEC_SCHEMA = {
    "local": {

        "algorithm": {
            "type": "string",
            "enum": ["paris-traceroute"]
        },

        "probe-type": {
            "type": "string",
            "enum": ["icmp", "udp", "tcp"]
        },

        "v1" : {
            "type": "object",
            "properties": {
                "schema":      { "type": "integer", "enum": [ 1 ] },
                "schema":      { "$ref": "#/pScheduler/Cardinal" },
                "algorithm":   { "$ref": "#/local/algorithm" },
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
                "schema":      { "$ref": "#/pScheduler/Cardinal" },
                "algorithm":   { "$ref": "#/local/algorithm" },
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
    schema = input_json.get("schema", 1)
    if type(schema) != int:
        return (False, "Invalid schema; must be an integer.")

    # Build a temporary structure with a reference that points
    # directly at the validator for the specified version of the
    # schema.  Using oneOf or anyOf results in error messages that are
    # difficult to decipher.

    temp_schema = {
        "local": SPEC_SCHEMA["local"],
        "$ref":"#/local/v%d" % schema
    }

    return json_validate(input_json, temp_schema)



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
            },
        "required": [
            "paths",
            "succeeded",
            ]
        }
    return json_validate(json, schema)



def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Cardinal" },
            "source":     { "$ref": "#/pScheduler/Limit/IPCIDRList"},
            "dest":       { "$ref": "#/pScheduler/Limit/IPCIDRList"},
            "endpoint":   { "$ref": "#/pScheduler/Limit/IPCIDRList"},
            "algorithm":  { "$ref": "#/pScheduler/Limit/String" },
            "as":         { "$ref": "#/pScheduler/Limit/Boolean" },
            "dest-port":  { "$ref": "#/pScheduler/Limit/Cardinal" },
            "first-ttl":  { "$ref": "#/pScheduler/Limit/Cardinal" },
            "fragment":   { "$ref": "#/pScheduler/Limit/Boolean" },
            "hops":       { "$ref": "#/pScheduler/Limit/Cardinal" },
            "hostnames":  { "$ref": "#/pScheduler/Limit/Boolean" },
            "ip-version": { "$ref": "#/pScheduler/Limit/CardinalList" },
            "length":     { "$ref": "#/pScheduler/Limit/Cardinal" },
            "probe-type": { "$ref": "#/pScheduler/Limit/String" },
            "queries":    { "$ref": "#/pScheduler/Limit/Cardinal" },
            "sendwait":   { "$ref": "#/pScheduler/Limit/Duration" },
            "ip-tos":     { "$ref": "#/pScheduler/Limit/CardinalZeroList" },
            "wait":       { "$ref": "#/pScheduler/Limit/Duration" }
        },
        "additionalProperties": False
        }

    return json_validate(json, schema)
