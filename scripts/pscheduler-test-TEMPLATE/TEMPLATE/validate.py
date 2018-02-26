#
# Validator for 'TEMPLATE' Test
#

# TODO: _ for sensitive values

from pscheduler import json_validate

def spec_is_valid(json):

    # SNMPv1Spec is valid for both snmp v1 and v2c 
    schema = {
            "Example Spec": {
                "type": "object",
                "properties": {
                    # Check datatype of the argument.
                    # Custom datatypes can be defined within this file.
                    "example":       { "$ref": "#/pScheduler/String" }
                },
                # Required arguments
                "required": [
                    "example"
                    ]
            }
        },
        "additionalProperties": True
    }

    return json_validate(json, schema)

def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            # Verify that each part of the result has its expected datatype.
            # For example:
            "time":       { "$ref": "#/pScheduler/Duration" },
            },
        "required": [
            "time"
            ]
        }
    return json_validate(json, schema)

def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            # Verify that the set limits have their expected datatype.
            "type":           { "$ref": "#/pScheduler/Limit/String" },
        },
        "additionalProperties": False
        }

    return json_validate(json, schema)
