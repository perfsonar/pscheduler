#
# Validator for "trace" Test
#

from pscheduler import json_validate

def spec_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":            { "$ref": "#/pScheduler/Cardinal" },
            "count":             { "$ref": "#/pScheduler/Cardinal" },
            "dest":              { "$ref": "#/pScheduler/Host" },
            # TODO: This is supposed to be a 20-bit number.  Validate that.
            "flow-label":        { "$ref": "#/pScheduler/CardinalZero" },
            "hostnames":         { "$ref": "#/pScheduler/Boolean" },
            "interval":          { "$ref": "#/pScheduler/Duration" },
            "ip-version":        { "$ref": "#/pScheduler/ip-version" },
            "source":            { "$ref": "#/pScheduler/Host" },
            "suppress-loopback": { "$ref": "#/pScheduler/Boolean" },
            "tos":               { "$ref": "#/pScheduler/Cardinal" },
            "length":            { "$ref": "#/pScheduler/Cardinal" },
            "ttl":               { "$ref": "#/pScheduler/Cardinal" },
            "deadline":          { "$ref": "#/pScheduler/Duration" },
            "timeout":           { "$ref": "#/pScheduler/Duration" },
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
            "roundtrip": {
                "type": "object",
                "properties": {
                    "ip": { "$ref": "#/pScheduler/IPAddress" },
                    "length": { "$ref": "#/pScheduler/Cardinal" },
                    "rtt": { "$ref": "#/pScheduler/Duration" },
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
            "loss": { "$ref": "#/pScheduler/Probability" },
            "min": { "$ref": "#/pScheduler/Duration" },
            "max": { "$ref": "#/pScheduler/Duration" },
            "mean": { "$ref": "#/pScheduler/Duration" },
            "stddev": { "$ref": "#/pScheduler/Duration" }
            },
        "required": [
            "schema",
            "succeeded",
            "roundtrips",
            "loss",
            ]
        }
    return json_validate(json, schema)
