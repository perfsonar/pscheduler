#
# Validator for a pScheduler test and its result.
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate_from_standard_template
from pscheduler import json_validate
import pscheduler


#
# Test Result
#

RESULT_SCHEMA = {

    "local": {
        # Define any local types here.
    },

    "versions": {

        "1": {
            "type": "object",
            "properties": {
                "schema":     { "type": "integer", "enum": [ 1 ] },
                "succeeded":  { "$ref": "#/pScheduler/Boolean" },
                "time":       { "$ref": "#/pScheduler/Duration" },
                "ipv4": {
                    "type": "array",
                    "items": { "$ref": "#/pScheduler/IPv4" },
                "minItems" : 0
                },
                "ipv6": {
                    "type": "array",
                    "items": {"$ref": "#/pScheduler/IPv6"},
                    "minItems": 0
                },
                "translated": { "$ref": "#/pScheduler/Boolean" },
            },
            "required": [
                "succeeded",
                "time",
            ],
            "additionalProperties": False
        }

    }

}


def result_is_valid(json):
    return json_validate_from_standard_template(json, RESULT_SCHEMA)
