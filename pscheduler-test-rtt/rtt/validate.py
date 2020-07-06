#
# Validator for "rtt" Test
#

from pscheduler import json_validate

MAX_SCHEMA = 3

def spec_is_valid(json):
    SPEC_SCHEMA = {
        "local" : {
            "protocol": {
                "type": "string",
                "enum": ["icmp", "twamp"]
            },
            "v1": {
                "type": "object",
                "properties": {
                    "schema":            { "$ref": "#/pScheduler/Cardinal", "enum": [ 1 ] },
                    "count":             { "$ref": "#/pScheduler/Cardinal" },
                    "dest":              { "$ref": "#/pScheduler/Host" },
                    # There is no dest-node because this is a one-participant test.
                    # TODO: This is supposed to be a 20-bit number.  Validate that.
                    "flow-label":        { "$ref": "#/pScheduler/CardinalZero" },
                    "hostnames":         { "$ref": "#/pScheduler/Boolean" },
                    "interval":          { "$ref": "#/pScheduler/Duration" },
                    "ip-version":        { "$ref": "#/pScheduler/ip-version" },
                    "source":            { "$ref": "#/pScheduler/Host" },
                    "source-node":       { "$ref": "#/pScheduler/URLHostPort" },
                    "suppress-loopback": { "$ref": "#/pScheduler/Boolean" },
                    "ip-tos":            { "$ref": "#/pScheduler/IPTOS" },
                    "length":            { "$ref": "#/pScheduler/Cardinal" },
                    "ttl":               { "$ref": "#/pScheduler/Cardinal" },
                    "deadline":          { "$ref": "#/pScheduler/Duration" },
                    "timeout":           { "$ref": "#/pScheduler/Duration" },
                    },
                "required": [
                    "dest"
                    ],
                "additionalProperties": False
            },
            "v2": {
                "type": "object",
                "properties": {
                    "schema":            { "$ref": "#/pScheduler/Cardinal", "enum": [ 2 ] },
                    "count":             { "$ref": "#/pScheduler/Cardinal" },
                    "dest":              { "$ref": "#/pScheduler/Host" },
                    # There is no dest-node because this is a one-participant test.
                    # TODO: This is supposed to be a 20-bit number.  Validate that.
                    "flow-label":        { "$ref": "#/pScheduler/CardinalZero" },
                    "hostnames":         { "$ref": "#/pScheduler/Boolean" },
                    "interval":          { "$ref": "#/pScheduler/Duration" },
                    "ip-version":        { "$ref": "#/pScheduler/ip-version" },
                    "source":            { "$ref": "#/pScheduler/Host" },
                    "source-node":       { "$ref": "#/pScheduler/URLHostPort" },
                    "suppress-loopback": { "$ref": "#/pScheduler/Boolean" },
                    "ip-tos":            { "$ref": "#/pScheduler/IPTOS" },
                    "length":            { "$ref": "#/pScheduler/Cardinal" },
                    "ttl":               { "$ref": "#/pScheduler/Cardinal" },
                    "deadline":          { "$ref": "#/pScheduler/Duration" },
                    "timeout":           { "$ref": "#/pScheduler/Duration" },
                    "protocol":          { "$ref": "#/local/protocol" },
                    },
                "required": [
                    "schema",
                    "dest"
                    ],
                "additionalProperties": False
            },
            "v3": {
                "type": "object",
                "properties": {
                    "schema":            { "$ref": "#/pScheduler/Cardinal", "enum": [ 3 ] },
                    "count":             { "$ref": "#/pScheduler/Cardinal" },
                    "dest":              { "$ref": "#/pScheduler/Host" },
                    # There is no dest-node because this is a one-participant test.
                    # TODO: This is supposed to be a 20-bit number.  Validate that.
                    "flow-label":        { "$ref": "#/pScheduler/CardinalZero" },
                    "fragment":          { "$ref": "#/pScheduler/Boolean" },
                    "hostnames":         { "$ref": "#/pScheduler/Boolean" },
                    "interval":          { "$ref": "#/pScheduler/Duration" },
                    "ip-version":        { "$ref": "#/pScheduler/ip-version" },
                    "source":            { "$ref": "#/pScheduler/Host" },
                    "source-node":       { "$ref": "#/pScheduler/URLHostPort" },
                    "suppress-loopback": { "$ref": "#/pScheduler/Boolean" },
                    "ip-tos":            { "$ref": "#/pScheduler/IPTOS" },
                    "length":            { "$ref": "#/pScheduler/Cardinal" },
                    "ttl":               { "$ref": "#/pScheduler/Cardinal" },
                    "deadline":          { "$ref": "#/pScheduler/Duration" },
                    "timeout":           { "$ref": "#/pScheduler/Duration" },
                    "protocol":          { "$ref": "#/local/protocol" },
                    },
                "required": [
                    "schema",
                    "dest"
                    ],
                "additionalProperties": False
            },
        }
    }


    # Build a temporary structure with a reference that points
    # directly at the validator for the specified version of the
    # schema.  Using oneOf or anyOf results in error messages that are
    # difficult to decipher.

    temp_schema = {
        "local": SPEC_SCHEMA["local"],
        "$ref":"#/local/v%d" % json.get("schema", 1)
    }

    return json_validate(json, temp_schema, max_schema=MAX_SCHEMA)


def result_is_valid(json):
    schema = {
        "local": {
            "roundtrip": {
                "type": "object",
                "properties": {
                    "ip": { "$ref": "#/pScheduler/IPAddress" },
                    "length": { "$ref": "#/pScheduler/Cardinal" },
                    "rtt": { "$ref": "#/pScheduler/Duration" },
                    "ttl": { "$ref": "#/pScheduler/Cardinal" },
                    "seq": { "$ref": "#/pScheduler/Cardinal" },
                    "error": { "$ref": "#/pScheduler/icmp-error" },
                    },
                "required": [
                    # Nothing required.
                    ]
                }
            },

        "type": "object",
        "properties": {
            "schema": { "$ref": "#/pScheduler/Cardinal" },
            "succeeded": { "$ref": "#/pScheduler/Boolean" },
            "roundtrips": {
                "type": "array",
                "items": { "$ref": "#/local/roundtrip" },
                },
            "sent": { "$ref": "#/pScheduler/Cardinal" },
            "received": { "$ref": "#/pScheduler/CardinalZero" },
            "lost": { "$ref": "#/pScheduler/CardinalZero" },
            "reorders": { "$ref": "#/pScheduler/CardinalZero" },
            "duplicates": { "$ref": "#/pScheduler/CardinalZero" },
            "loss": { "$ref": "#/pScheduler/Probability" },
            "min": { "$ref": "#/pScheduler/Duration" },
            "max": { "$ref": "#/pScheduler/Duration" },
            "mean": { "$ref": "#/pScheduler/Duration" },
            "stddev": { "$ref": "#/pScheduler/Duration" }
            },
        "required": [
            "succeeded",
            "roundtrips",
            "loss",
            ]
        }
    return json_validate(json, schema)


def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":            { "$ref": "#/pScheduler/Cardinal" },
            "source":            { "$ref": "#/pScheduler/Limit/IPCIDRList"},
            "dest":              { "$ref": "#/pScheduler/Limit/IPCIDRList"},
            "endpoint":          { "$ref": "#/pScheduler/Limit/IPCIDRList"},
            "count":             { "$ref": "#/pScheduler/Limit/Cardinal" },
            "flow-label":        { "$ref": "#/pScheduler/Limit/CardinalZeroList" },
            "hostnames":         { "$ref": "#/pScheduler/Limit/Boolean" },
            "interval":          { "$ref": "#/pScheduler/Limit/Duration" },
            "ip-version":        { "$ref": "#/pScheduler/Limit/IPVersionList" },
            "suppress-loopback": { "$ref": "#/pScheduler/Limit/Boolean" },
            "ip-tos":            { "$ref": "#/pScheduler/Limit/CardinalList" },
            "length":            { "$ref": "#/pScheduler/Limit/Cardinal" },
            "ttl":               { "$ref": "#/pScheduler/Limit/Cardinal" },
            "deadline":          { "$ref": "#/pScheduler/Limit/Duration" },
            "timeout":           { "$ref": "#/pScheduler/Limit/Duration" }
        },
        "additionalProperties": False
        }

    return json_validate(json, schema)
