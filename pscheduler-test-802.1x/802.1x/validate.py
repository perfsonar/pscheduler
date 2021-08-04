#
# Validator for "802.1x" Test
#

from pscheduler import json_validate


def spec_is_valid(json):
    schema = {
        "local": {
            "eap_type": {
                "type": "string",
                "enum": ["PEAP", "MD5"]
            }
        },
        "type": "object",
        "properties": {
            "schema":    {"$ref": "#/pScheduler/Cardinal"},
            "timeout":   {"$ref": "#/pScheduler/Duration"},
            "interface": {"$ref": "#/pScheduler/String"},
            "eap_type":  {"$ref": "#/local/eap_type"},
            "_username":  {"$ref": "#/pScheduler/String"},
            "_password":  {"$ref": "#/pScheduler/String"},
            "auth_inner":  {"$ref": "#/pScheduler/String"},
            "auth_outer":  {"$ref": "#/pScheduler/String"},
        },
        "required": [
            "interface",
            "eap_type",
            "_username",
            "_password"
        ]
    }

    return json_validate(json, schema)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     {"$ref": "#/pScheduler/Cardinal"},
            "succeeded":  {"$ref": "#/pScheduler/Boolean"},
            "bssid":      {"$ref": "#/pScheduler/String"},
            "mac_addr":   {"$ref": "#/pScheduler/String"},
            "ip_addr":    {"$ref": "#/pScheduler/String"},
        },
        "required": [
            "schema",
            "succeeded"
        ]
    }

    return json_validate(json, schema)
