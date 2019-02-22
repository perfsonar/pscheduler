#
# Validator for "rtt" Test
#

from pscheduler import json_validate

def spec_is_valid(json):
    schema = {
        "local" : {
            "protocol": {
                "type": "string",
                "enum": ["icmp", "twamp"]
            },
            "rtt_v1": {
                "type": "object",
                "properties": {
                    "schema":            { "$ref": "#/pScheduler/Cardinal" },
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
            "rtt_v2": {
                "type": "object",
                "properties": {
                    "schema":            { "$ref": "#/pScheduler/Cardinal" },
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
                    "dest"
                    ],
                "additionalProperties": False
            },
            "rtt_v3": {
                "type": "object",
                "properties": {
                    "schema":            { "$ref": "#/pScheduler/Cardinal" },
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
                    "dest"
                    ],
                "additionalProperties": False
            },
            "rtt": {
                "anyOf": [
                    { "$ref": "#/local/rtt_v1" },
                    { "$ref": "#/local/rtt_v2" },
                    { "$ref": "#/local/rtt_v3" }
                ]
            }
        },

        "$ref": "#/local/rtt"
    }

    return json_validate(json, schema)


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
