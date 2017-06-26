#
# Validator for "trace" Test
#

from pscheduler import json_validate

def spec_is_valid(json):
    schema = {
        "local": {
            "algorithm": {
                "type": "string",
                "enum": ["paris-traceroute"]
                },
            "probe-type": {
                "type": "string",
                "enum": ["icmp", "udp", "tcp"]
                }
            },
        "type": "object",
        "properties": {
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
            "wait":        { "$ref": "#/pScheduler/Duration" },
            },
        "required": [
            "dest"
            ]
        }
    return json_validate(json, schema)


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
            "schema": { "$ref": "#/pScheduler/Cardinal" },
            "algorithm":  { "$ref": "#/pScheduler/Limit/String" },
            "as":         { "$ref": "#/pScheduler/Limit/Boolean" },
            "dest-port":  { "$ref": "#/pScheduler/Limit/Cardinal" },
            "dest":       { "$ref": "#/pScheduler/Limit/String" },
            "first-ttl":  { "$ref": "#/pScheduler/Limit/Cardinal" },
            "fragment":   { "$ref": "#/pScheduler/Limit/Boolean" },
            "hops":       { "$ref": "#/pScheduler/Limit/Cardinal" },
            "hostnames":  { "$ref": "#/pScheduler/Limit/Boolean" },
            "ip-version": { "$ref": "#/pScheduler/Limit/CardinalList" },
            "length":     { "$ref": "#/pScheduler/Limit/Cardinal" },
            "probe-type": { "$ref": "#/pScheduler/Limit/String" },
            "queries":    { "$ref": "#/pScheduler/Limit/Cardinal" },
            "sendwait":   { "$ref": "#/pScheduler/Limit/Duration" },
            "source":     { "$ref": "#/pScheduler/Limit/String" },
            "tos":        { "$ref": "#/pScheduler/Limit/CardinalZeroList" },
            "wait":       { "$ref": "#/pScheduler/Limit/Duration" }
        },
        "additionalProperties": False
        }

    return json_validate(json, schema)
