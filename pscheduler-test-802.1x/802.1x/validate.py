
#
# Validator for "802.1x" Test
#

from pscheduler import json_validate


def spec_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":    {"$ref": "#/pScheduler/Cardinal"},
            "timeout":   {"$ref": "#/pScheduler/Duration"},
            "interface": {"$ref": "#/pScheduler/String"},
            "eap_type":  {"$ref": "#/pScheduler/String"},
            "username":  {"$ref": "#/pScheduler/String"},
            "password":  {"$ref": "#/pScheduler/String"},
        },
        "required": [
            "interface",
            "eap_type",
            "username",
            "password"
        ]
    }

    return json_validate(json, schema)


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     {"$ref": "#/pScheduler/Cardinal"},
            "succeeded":  {"$ref": "#/pScheduler/Boolean"},
            "supplicant": {"$ref": "#/pScheduler/String"},
            "dhclient":   {"$ref": "#/pScheduler/String"},
            "bssid":      {"$ref": "#/pScheduler/String"},
            "mac_addr":   {"$ref": "#/pScheduler/String"},
            "ip_addr":    {"$ref": "#/pScheduler/String"},
        },
        "required": [
            # "duration",
            # "succeeded",
            # "supplicant",
            # "dhclient"
        ]
    }

    return json_validate(json, schema)


def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":    {"$ref": "#/pScheduler/Cardinal"},
            "time":      {"$ref": "#/pScheduler/Duration"},
            "interface": {"$ref": "#/pScheduler/String"},
            "eap_type":  {"$ref": "#/pScheduler/String"},
            "username":  {"$ref": "#/pScheduler/String"},
            "password":  {"$ref": "#/pScheduler/String"},
            "timeout":   {"$ref": "#/pScheduler/Limit/Duration"}
        },
        "additionalProperties": False
    }

    return json_validate(json, schema)
