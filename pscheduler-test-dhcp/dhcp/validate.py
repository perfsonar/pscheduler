#
# Validator for a pScheduler Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate

MAX_SCHEMA = 1

def spec_is_valid(json):

    schema = {
        "local": {},
            # Local data types such as this can be defined within this file,
            # but are not necessary
	"type": "object",
	# schema, host, host-node, and timeout are standard,
	# and should be included
	"properties": {
	    "schema":       { "$ref": "#/pScheduler/Cardinal" },
	    "host":         { "$ref": "#/pScheduler/Host" },
	    "host-node":    { "$ref": "#/pScheduler/Host" },
	    "timeout":      { "$ref": "#/pScheduler/Duration" },
	    "interface":    { "$ref": "#/pScheduler/AnyJSON" },
	},
	# If listed here, data of this type MUST be in the test spec
	"required": [],
    
        # Set to false if ONLY required options should be used
        "additionalProperties": False
    }

    return json_validate(json, schema, max_schema=MAX_SCHEMA)

def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":  { "$ref": "#/pScheduler/Boolean" },
            "time":       { "$ref": "#/pScheduler/Duration" },
            "ip_address": { "$ref": "#/pScheduler/AnyJSON" },
            },
        "required": [
            "time",
            "ip_address",
            ]
        }
    return json_validate(json, schema)
