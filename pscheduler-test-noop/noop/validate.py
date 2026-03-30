#
# Validator for "noop" Test
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
            "schema":           { "$ref": "#/pScheduler/Cardinal" },
            "data":             { "$ref": "#/pScheduler/AnyJSON" },
            "succeeded":        { "$ref": "#/pScheduler/Boolean" }
            },
        "additionalProperties": False,
        "required": [
            "data",
            "succeeded",
            ]
        }
    return json_validate(json, schema)
