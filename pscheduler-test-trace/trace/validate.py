#
# Validator for "trace" Test
#

from pscheduler import json_validate

def spec_is_valid(json):
    schema = {
        "local": {
            "probe-type": {
                "type": "string",
                "enum": ['icmp', 'udp', 'tcp']
                }
            },
        "type": "object",
        "properties": {
            "as":          { "$ref": "#/pScheduler/Boolean" },
            "dest-port":   { "$ref": "#/pScheduler/IPPort" },
            "dest":        { "$ref": "#/pScheduler/Host" },
            "first-ttl":   { "$ref": "#/pScheduler/Cardinal" },
            "fragment":    { "$ref": "#/pScheduler/Boolean" },
            "hops":        { "$ref": "#/pScheduler/Cardinal" },
            "hostnames":   { "$ref": "#/pScheduler/Boolean" },
            "ip-version":  { "$ref": "#/pScheduler/ip-version" },
            "length":      { "$ref": "#/pScheduler/Cardinal" },
            "probe-type":  { "$ref": "#/local/probe-type" },
            "schema":      { "$ref": "#/pScheduler/Cardinal" },
            "sendwait":    { "$ref": "#/pScheduler/Duration" },
            "source":      { "$ref": "#/pScheduler/Host" },
            # TODO: This should be changed to whatever we come up with for TOS
            "tos":         { "$ref": "#/pScheduler/Cardinal" },
            "wait":        { "$ref": "#/pScheduler/Duration" },
            },
        "required": [
            "schema",
            "dest",
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
                    "host": { "$ref": "#/pScheduler/Host" },
                    "rtt": { "$ref": "#/pScheduler/Duration" },
                    "as": { "$ref": "#/pScheduler/Cardinal" },
                    "error": { "$ref": "#/pScheduler/icmp-error" },
                    },
                "required": [
                    # Nothing required.
                    ]
                }
            },

        "type": "object",
        "properties": {
            "hops": {
                "type": "array",
                "items": { "$ref": "#/local/hop" },
                },
            "schema": { "$ref": "#/pScheduler/Cardinal" },
            "succeeded": { "$ref": "#/pScheduler/Boolean" },
            },
        "required": [
            "hops",
            "schema",
            "succeeded",
            ]
        }
    return json_validate(json, schema)
