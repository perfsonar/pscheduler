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

MAX_SCHEMA = 1

log = pscheduler.Log(prefix='test-dns64')

#
# Test Specification
#

# NOTE: A large dictionary of existing, commonly-used datatypes used
# throughout pScheduler is defined in
# pscheduler/python-pscheduler/pscheduler/pscheduler/jsonval.py.
# Please use those where possible.

SPEC_SCHEMA = {
    
    "local": {

        # Define any local types used in the spec here

    },

    "versions": {

        # Initial version of the specification
        "1": {
            "type": "object",
            # schema, host, host-node, and timeout are standard and
            # should be included in most single-participant tests.
            "properties": {
                "schema":            { "$ref": "#/pScheduler/Cardinal", "enum": [ 1 ] },
                "query":           { "$ref": "#/pScheduler/URL" },
                "nameserver":      { "$ref": "#/pScheduler/Host" },
                "host":           { "$ref": "#/pScheduler/Host" },
                "host-node":           { "$ref": "#/pScheduler/Host" },
                "translation-prefix":       { "$ref": "#/pScheduler/String" },
                "timeout":        { "$ref": "#/pScheduler/Duration" },
            },
            # If listed here, these parameters MUST be in the test spec.
            "required": [
                "query"
            ],
            # Treat other properties as acceptable.  This should
            # ALWAYS be false.
            "additionalProperties": False
        },

        # Second and later versions of the specification
        # "2": {
        #    "type": "object",
        #    "properties": {
        #        "schema": { "type": "integer", "enum": [ 2 ] },
        #        ...
        #    },
        #    "required": [
        #        "schema",
        #        ...
        #    ],
        #    "additionalProperties": False
        #},

    }

}



def spec_is_valid(json):

    (valid, errors) = json_validate_from_standard_template(json, SPEC_SCHEMA)
    #return json_validate(json, SPEC_SCHEMA, max_schema=MAX_SCHEMA)
    log.debug(json)

    if not valid:
        return (valid, errors)

    return (valid, errors)



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
