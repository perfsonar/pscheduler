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
# Test Specification
#

# NOTE: A large dictionary of existing, commonly-used datatypes used
# throughout pScheduler is defined in
# pscheduler/python-pscheduler/pscheduler/pscheduler/jsonval.py.
# Please use those where possible.

SPEC_SCHEMA = {
    
    "local": {
        
        # Define any local types used in the spec here
        "TestImplementation": {
            "type": "string",
            "enum": [ "system", "api" ]
        },

    },
    
    "versions": {
        
        # Initial version of the specification
        "1": {
            "type": "object",
            # schema, host, host-node, and timeout are standard and
            # should be included in most single-participant tests.
            "properties": {
                # The schema should always be constrained to a single
                # value per version.
                "schema":         { "type": "integer", "enum": [ 1 ] },
                "query":           { "$ref": "#/pScheduler/Host" },
                "nameserver":      { "$ref": "#/pScheduler/Host" },
                "host":           { "$ref": "#/pScheduler/Host" },
                "host-node":           { "$ref": "#/pScheduler/Host" },
                "translation-prefix":       { "$ref": "#/pScheduler/String" },
                "timeout":        { "$ref": "#/pScheduler/Duration" },
            },
            # If listed here, these parameters MUST be in the test spec.
            "required": [
                "query",
                "nameserver",
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

    if not valid:
        return (valid, errors)

    # If there are semantic relationships that can't be expressed the
    # JSON Schema (e.g., parameter X can't be less then 5 when
    # parameter Y is an odd number), evaluate them here and complain
    # if there's a problem.  E.g.,:
    #
    #if some_condition_which_is_an_error
    #    return(False, "...Error Message...")

    # By this point, everything is okay.
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
                "ipv4 address": { "$ref": "#/pScheduler/Host" },
                "ipv6 address": { "$ref": "#/pScheduler/Host" },
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
