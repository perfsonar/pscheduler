#
# Validator for "snmpget" Test
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
            "succeeded":  { "$ref": "#/pScheduler/Boolean" },
            "error":      { "$ref": "#/pScheduler/String" },
            "diags":      { "$ref": "#/pScheduler/String" },
            "time":       { "$ref": "#/pScheduler/Duration" },
            "data":       { "type": "array",
                            "items": { "$ref": "#/pScheduler/SNMPResultList" } 
                          },
            },
        "required": [
            "schema",
            "succeeded",
            "data",
            "time",
            ]
        }

    return json_validate(json, schema, max_schema=MAX_SCHEMA)
