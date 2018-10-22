#
# Validator for "netreach" Test
#

from pscheduler import json_validate

# TODO: Need host, host-node, possibly binding...

def spec_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":            { "$ref": "#/pScheduler/Cardinal" },
            "gateway":           { "$ref": "#/pScheduler/Host" },
            "network":           { "$ref": "#/pScheduler/IPCIDR" },
            "parallel":          { "$ref": "#/pScheduler/Cardinal" },
            "timeout":           { "$ref": "#/pScheduler/Duration" }
            },
        "required": [
            "network"
            ]
        }
    return json_validate(json, schema)


def result_is_valid(json):
    schema = {
	"type": "object",
        "properties": {
            "schema":       { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":    { "$ref": "#/pScheduler/Boolean" },
            "gateway-up":   { "$ref": "#/pScheduler/Boolean" },
            "network-up":   { "$ref": "#/pScheduler/Boolean" }
            },
        "required": [ "succeeded", "network-up" ]
        }
    return json_validate(json, schema)
