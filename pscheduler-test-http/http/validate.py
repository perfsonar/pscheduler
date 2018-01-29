#
# Validator for "snmpset" Test
#

# TODO: _ for sensitive values

from pscheduler import json_validate

def spec_is_valid(json):

    # SNMPv1Spec is valid for both snmp v1 and v2c 
    schema = {
        "local": {
            "URLSpec": {
                "type": "object",
                "properties": {
                    "schema":       { "$ref": "#/pScheduler/Cardinal" },
                    "host":         { "$ref": "#/pScheduler/Host" },
                    "host-node":    { "$ref": "#/pScheduler/Host" },
                    "url":          { "$ref": "#/pScheduler/String" },
                    "timeout":      { "$ref": "#/pScheduler/Duration" },
                },
                "required": [
                    "url",
                    ]
            },
        },
        "additionalProperties": True
    }

    return json_validate(json, schema)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":  { "$ref": "#/pScheduler/Boolean" },
            "time":       { "$ref": "#/pScheduler/Duration" },
            "data":       { "$ref": "#/pScheduler/Float" },

        "required": [
            "schema",
            "succeeded",
            "data",
            "time",
            ]
        }
    }
    return json_validate(json, schema)

def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "url":          { "$ref": "#/pScheduler/Limit/String" },
            "host":            { "$ref": "#/pScheduler/Limit/String" },
            "host-node":     { "$ref": "#/pScheduler/Limit/String" },
            "timeout":         { "$ref": "#/pScheduler/Limit/Duration" },
            "type":           { "$ref": "#/pScheduler/Limit/String" },
            "value":           { "$ref": "#/pScheduler/Limit/String" },
        },
        "additionalProperties": False
        }

    return json_validate(json, schema)
