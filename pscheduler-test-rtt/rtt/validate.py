#
# Validator for "rtt" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate

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
            "error": { "$ref": "#/pScheduler/String" },
            "diags": { "$ref": "#/pScheduler/String" },
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
