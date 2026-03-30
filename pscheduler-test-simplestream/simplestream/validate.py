#
# Validator for "simplestream" Test
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
            "schema":         { "$ref": "#/pScheduler/Cardinal" },
            "dawdled":       { "$ref": "#/pScheduler/Duration" },
            "elapsed-time":  { "$ref": "#/pScheduler/Duration" },
            "received":      { "$ref": "#/pScheduler/String" },
            "sent":          { "$ref": "#/pScheduler/String" },
            "succeeded":     { "$ref": "#/pScheduler/Boolean" },
            "error":         { "$ref": "#/pScheduler/String" },
            "diags":         { "$ref": "#/pScheduler/String" }
            },
        "required": [
            "dawdled",
            "elapsed-time",
            "received",
            "sent",
            "succeeded",
            ]
        }
    return json_validate(json, schema)
