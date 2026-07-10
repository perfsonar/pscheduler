#
# Validator for "s3throughput" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate_from_standard_template
from pscheduler import json_standard_template_max_schema



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
                "schema":              { "type": "integer", "enum": [ 1 ] },
                "succeeded":           { "$ref": "#/pScheduler/Boolean" },
	        "error":               { "$ref": "#/pScheduler/String" },
	        "diags":               { "$ref": "#/pScheduler/String" },
	        "loops":               { "$ref": "#/pScheduler/String" },
	        "average_put_time":    { "$ref": "#/pScheduler/Float" },
	        "average_get_time":    { "$ref": "#/pScheduler/Float" },
	        "average_delete_time": { "$ref": "#/pScheduler/Float" },
                "time" :               { "$ref": "#/pScheduler/Duration" }    
	    },
            "required": [
                "succeeded",
	        "average_put_time",
	        "average_get_time",
	        "average_delete_time"
            ]
        }
    }
}


def result_max_schema():
    return json_standard_template_max_schema(RESULT_SCHEMA)


def result_is_valid(json):
    return json_validate_from_standard_template(json, RESULT_SCHEMA)
