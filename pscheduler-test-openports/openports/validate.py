#
# Validator for a pScheduler Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate

def check_spec_semantics(proposed):
    '''
    This checks that the spec is semantically-valid.  It is safe to
    assume that validation of the JSON passed.
    '''

    # TODO: This is untested.

    #Verify Port Order is valid
    if proposed.get("ports") is None:
        return(True, 'OK')

    portlist = proposed.get("ports").split(",")
    allports = []
    for ele in portlist:
        begin = end = ele
        if "-" in ele:
            (begin, end) = ele.split("-")
            if int(end) < int(begin):
                pscheduler.succeed_json({
                    "valid": False,
                    "error": "Port range is backwards. Did you mean " + end + "-" + begin +"?"
                })
        for port in range(int(begin), int(end)+1):
            newports = []
            if port in allports:
                pscheduler.succeed_json({
                "valid": False,
                "error": "Duplicate value in port list: " + str(port)
                })
            newports.append(port)
        allports+=newports


def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":  { "$ref": "#/pScheduler/Boolean" },
            "result":     {
                "succeeded":  { "$ref": "#/pScheduler/Boolean" },
                "result":     { "$ref": "#/pScheduler/AnyJSON" },
                "error":      { "$ref": "#/pScheduler/String" },
                "diags":      { "$ref": "#/pScheduler/String" }
                },
            "error":      { "$ref": "#/pScheduler/String" },
            "diags":      { "$ref": "#/pScheduler/String" }
            },
        "required": [
            "succeeded",
            "result"
            ]
        }
    return json_validate(json, schema)
