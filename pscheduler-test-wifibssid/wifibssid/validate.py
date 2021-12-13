#
# Validator for a pScheduler test and its result.
#

#
# Development Order #3: Test specification and result validation
#
# The functions in this file determine whether or not specifications
# and results for this test are valid.
#


from pscheduler import json_validate_from_standard_template



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
                # The schema should always be constrained to a single
                # value per version.
                "schema":         { "type": "integer", "enum": [ 1 ] },
                "host":           { "$ref": "#/pScheduler/Host" },
                "host-node":      { "$ref": "#/pScheduler/Host" },
                "duration":       { "$ref": "#/pScheduler/Duration" },
                "timeout":        { "$ref": "#/pScheduler/Duration" },
		        "interface":      { "$ref": "#/pScheduler/String" },
		        "ssid":           { "$ref": "#/pScheduler/String" },
            },
            # If listed here, these parameters MUST be in the test spec.
            "required": [
                "interface",
		        "ssid",
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
