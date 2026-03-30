#
# Validator for "trace" Test
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
