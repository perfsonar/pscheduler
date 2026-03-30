#
# Validator for a pScheduler test and its result.
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate_from_standard_template

MAX_SCHEMA = 1


#
# Test Result
#

RESULT_SCHEMA = {

    "local": {
        # Define any local types here.
        "ssid_info": {
            "type": "object",
            "properties": {
                "ssid":      { "$ref": "#/pScheduler/String" },
                "signal":    { "type": "number" },
                "address":   { "$ref": "#/pScheduler/String" },
                "frequency": { "type": "number" },
                "quality":   { "type": "number" },
                "bitrates":  { "type": "array", "items": { "type": "number" } },
                "encrypted": { "$ref": "#/pScheduler/Boolean" },
                "channel":   { "$ref": "#/pScheduler/Cardinal" },
                "mode":      { "$ref": "#/pScheduler/String" },
            },
            "required": [
                "ssid",
                "signal",
                "address",
                "frequency",
                "quality",
                "bitrates",
                "encrypted",
                "channel",
                "mode",
            ],
            "additionalProperties": False
        }    
    },

    "versions": {

        "1": {
            "type": "object",
            "properties": {
                "schema":     { "type": "integer", "enum": [ 1 ] },
                "succeeded":  { "$ref": "#/pScheduler/Boolean" },
                "time":       { "$ref": "#/pScheduler/Duration" },
		"ssid_list":  { "type": "array", "items": { "local": "#/local/ssid_info" } },
            },
            "required": [
                "succeeded",
                "time",
		"ssid_list",
            ],
            "additionalProperties": False
        }

    }

}


def result_is_valid(json):
    return json_validate_from_standard_template(json, RESULT_SCHEMA)
