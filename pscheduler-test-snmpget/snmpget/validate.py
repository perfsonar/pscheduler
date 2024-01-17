#
# Validator for "snmpget" Test
#

from pscheduler import json_validate

MAX_SCHEMA = 1

def spec_is_valid(json):

    # SNMPv1Spec is valid for both snmp v1 and v2c 
    schema = {
        "local": {
            "VersionNumber": {
                "type": "string",
                "enum": [ "1", "2c", "3"]
            },
            "AuthProtocol": {
                "type": "string",
                "enum": [ "MD5", "SHA"]
            },
            "PrivProtocol": {
                "type": "string",
                "enum": [ "AES", "AES128", "AES192", "AES256", "DES", "3DES" ]
            },
            "SecurityLevel": {
                "type": "string",
                "enum": [ "noAuthNoPriv", "authNoPriv", "authPriv"]
            },
            "TransportProtocol": {
                "type": "string",
                "enum": ["tcp", "udp"]
            },
            "SNMPv1Spec": {
                "type": "object",
                "properties": {
                    "schema":       { "$ref": "#/pScheduler/Cardinal" },
                    "host":         { "$ref": "#/pScheduler/Host" },
                    "host-node":    { "$ref": "#/pScheduler/Host" },
                    "dest":         { "$ref": "#/pScheduler/Host" },
                    "version":      { "$ref": "#/local/VersionNumber"},
                    "_community":   { "$ref": "#/pScheduler/String"},
                    "period":       { "$ref": "#/pScheduler/Integer" },
                    "polls":        { "$ref": "#/pScheduler/Integer" },
                    "oid":          { "type": "array", 
                                      "items": { "$ref": "#/pScheduler/SNMPOID" },
                                      "minItems": 1,
                                    },
                    "protocol":     { "$ref": "#/local/TransportProtocol" },
                    "timeout":      { "$ref": "#/pScheduler/Duration" },
                },
                "required": [
                    "version",
                    "_community",
                    "dest",
                    "oid",
                    "polls"
                ],
                "additionalProperties": False
            },

            "SNMPv3Spec": {
                "type": "object",
                "properties": {
                    "schema":       { "$ref": "#/pScheduler/Cardinal" },
                    "host":         { "$ref": "#/pScheduler/Host" },
                    "host-node":    { "$ref": "#/pScheduler/Host" },
                    "dest":         { "$ref": "#/pScheduler/Host" },
                    "version":      { "$ref": "#/local/VersionNumber"},
                    "period":       { "$ref": "#/pScheduler/Integer" },
                    "polls":        { "$ref": "#/pScheduler/Integer" },
                    "oid":          { "type": "array", 
                                      "items": { "$ref": "#/pScheduler/SNMPOID" },
                                      "minItems": 1,
                                    },
                    "protocol":     { "$ref": "#/local/TransportProtocol" },
                    "security-name":   { "$ref": "#/pScheduler/String" },
                    "auth-protocol":   { "$ref": "#/local/AuthProtocol" },
                    "priv-protocol":   { "$ref": "#/local/PrivProtocol" },
                    "_auth-key":       { "$ref": "#/pScheduler/String" },
                    "_priv-key":       { "$ref": "#/pScheduler/String" },
                    "security-level":  { "$ref": "#/local/SecurityLevel" },
                    "context":         { "$ref": "#/pScheduler/String" },
                    "timeout":         { "$ref": "#/pScheduler/Duration" },
                },
                "required": [
                    "version",
                    "dest",
                    "oid",
                    "polls"
                ],
                "additionalProperties": False
            },

            "SNMPSpec": {
                "oneOf": [
                    { "$ref": "#/local/SNMPv1Spec" },
                    { "$ref": "#/local/SNMPv3Spec" }
                ],
            }
        
        },

        "$ref": "#/local/SNMPSpec"
    }

    return json_validate(json, schema, max_schema=MAX_SCHEMA)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":  { "$ref": "#/pScheduler/Boolean" },
            "error":      { "$ref": "#/pScheduler/String" },
            "diags":      { "$ref": "#/pScheduler/String" },
            "time":       { "$ref": "#/pScheduler/Duration" },
            "data":       { "$ref": "#/pScheduler/SNMPResultList" },
            },
        "required": [
            "succeeded",
            "data",
            "time",
            ]
        }
    return json_validate(json, schema)
