#
# Validator for "disk-to-disk" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate

MAX_SCHEMA = 1

def spec_is_valid(json):
    schema = {"type": "object",
                # schema, host, host-node, and timeout are standard,
                # and should be included
                "properties": {
                    "schema":       { "$ref": "#/pScheduler/Cardinal" },
                    "parallel":     { "$ref": "#/pScheduler/Cardinal" },
                    "host":         { "$ref": "#/pScheduler/Host"     },
                    "dest":         { "$ref": "#/pScheduler/String"   },
                    "source":       { "$ref": "#/pScheduler/String"   },
                    "duration":     { "$ref": "#/pScheduler/Duration" },
                    "timeout":      { "$ref": "#/pScheduler/Duration" },
                    "cleanup":      { "$ref": "#/pScheduler/Boolean"  },
                },
                # If listed here, data of this type MUST be in the test spec
                "required":  [
                    "dest", "source"
                    ],

        "additionalProperties": False
    }

    return json_validate(json, schema, max_schema=MAX_SCHEMA)


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
