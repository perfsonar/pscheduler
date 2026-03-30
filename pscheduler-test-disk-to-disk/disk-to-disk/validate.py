#
# Validator for "disk-to-disk" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":  { "$ref": "#/pScheduler/Boolean"  },
            "diags":      { "$ref": "#/pScheduler/String" },
            "error":      { "$ref": "#/pScheduler/String" },
            "time":       { "$ref": "#/pScheduler/Duration" },
            "bytes-sent": { "$ref": "#/pScheduler/Float" },
            "throughput": { "$ref": "#/pScheduler/Float" },
            },
        "required": [
            "succeeded",
            "time"
            ]
        }
    return json_validate(json, schema)
