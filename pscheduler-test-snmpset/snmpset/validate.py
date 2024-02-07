#
# Validator for "snmpset" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

# TODO: _ for sensitive values

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
                "enum": [ "md5", "sha"]
            },
            "PrivProtocol": {
                "type": "string",
                "enum": [ "aes", "des"]
            },
            "SecurityLevel": {
                "type": "string",
                "enum": [ "noauthnopriv", "authnopriv", "authpriv"]
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
                    "_community":    { "$ref": "#/pScheduler/String"},
                    "oid":          { "type": "array", 
                                      "items": { "$ref": "#/pScheduler/SNMPOID" } 
                                    },
                    "protocol":     { "$ref": "#/local/TransportProtocol" },
                    "timeout":      { "$ref": "#/pScheduler/Duration" },
                },
                "required": [
                    "version",
                    "_community",
                    "dest",
                    "oid"
                    ]
            },
            "SNMPv3Spec": {
                "type": "object",
                "properties": {
                    "schema":       { "$ref": "#/pScheduler/Cardinal" },
                    "host":         { "$ref": "#/pScheduler/Host" },
                    "host-node":    { "$ref": "#/pScheduler/Host" },
                    "dest":         { "$ref": "#/pScheduler/Host" },
                    "version":      { "$ref": "#/local/VersionNumber"},
                    "oid":          { "type": "array", 
                                      "items": { "$ref": "#/pScheduler/SNMPNumericOID" } 
                                    },
                    "protocol":     { "$ref": "#/local/TransportProtocol" },
                    "security-name":           { "$ref": "#/pScheduler/String" },
                    "auth-protocol":           { "$ref": "#/local/AuthProtocol" },
                    "priv-protocol":           { "$ref": "#/local/PrivProtocol" },
                    "auth-key":           { "$ref": "#/pScheduler/String" },
                    "priv-key":           { "$ref": "#/pScheduler/String" },
                    "security-level":           { "$ref": "#/local/SecurityLevel" },
                    "context":      { "$ref": "#/pScheduler/String" },
                    "timeout":      { "$ref": "#/pScheduler/Duration" },
                },
                "required": [
                    "version",
                    "dest",
                    "oid"
                    ]
            }
        
        },
        "oneOf": [
            { "$ref": "#/local/SNMPv1Spec" },
            { "$ref": "#/local/SNMPv3Spec" }
        ],
        "additionalProperties": True
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
            "data":       { "type": "array",
                            "items": { "$ref": "#/pScheduler/SNMPResult" } 
                          },
            },
        "required": [
            "schema",
            "succeeded",
            "data",
            "time",
            ]
        }
    return json_validate(json, schema)
