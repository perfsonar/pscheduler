"""
Limit Class for test-type
"""

import pscheduler


test_data_validator = {
    "type": "object",
    "properties": {
        "test": { "$ref": "#/pScheduler/String" },
        "limit": { "$ref": "#/pScheduler/AnyJSON" }
    },
    "additionalProperties": False,
    "required": [ "test", "limit" ]
}

def test_data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return pscheduler.json_validate(data, test_data_validator)



class LimitTest():

    """Limit that passes or fails based on whether or not a test says it
    does.
    """

    def __init__(self,
                 data   # Data suitable for this class
                 ):
       
        valid, message = test_data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.test = data['test']
        self.limit = data['limit']

        returncode, stdout, stderr = pscheduler.run_program(
            [ "pscheduler", "internal", "invoke", "test", self.test, "limit-is-valid" ],
            stdin = pscheduler.json_dump(self.limit),
            # TODO:  Is this reasonable?
            timeout = 5
            )

        if returncode != 0:
            raise RuntimeError("Failed to validate limit: %s" % stderr)

        result = pscheduler.json_load(stdout)
        if not result['valid']:
            raise ValueError("Invalid limit: %s" % result['message'])



    def evaluate(self,
                 run,            # The proposed run
                 check_schedule  # Keep/disregard time-related limits
                 ):

        # Dissent if the test isn't our type
        if run["type"] != self.test:
            return { "passed": False, "reasons": [ "Test is not '%s'" % self.test ] }

        pass_input = {
            "spec": run["spec"],
            "limit": self.limit
            }

        returncode, stdout, stderr = pscheduler.run_program(
            [ "pscheduler", "internal", "invoke", "test", self.test, "limit-passes" ],
            stdin = pscheduler.json_dump(pass_input),
            # TODO:  Is this reasonable?
            timeout = 5
            )

        if returncode != 0:
            raise RuntimeError("Failed to validate limit: %s" % stderr)

        check_result = pscheduler.json_load(stdout)
        passed = check_result["passes"]

        result = { "passed": passed }
        if not passed:
            result["reasons"] = check_result["errors"]

        return result



# A short test program

if __name__ == "__main__":

    limit = LimitTest({
        "test": "idle",
        "limit": {
            "duration": {
                "description": "Short-ish idleness.",
                "range": {
                    "lower": "PT15S",
                    "upper": "PT1M"
                },
                "invert": False
            },
            "starting-comment" : {
                "description": "Starting comment can't contain the word 'platypus'.",
                "match": {
                    "style": "regex",
                    "match": "platypus",
                    "case-insensitive": True,
                    "invert": True
                }
            },
            "parting-comment" : {
                "description": "Parting comment must contain a vowel if not empty", 
                "match": {
                    "style": "regex",
                    "match": "(^$|[aeiou])",
                    "case-insensitive": True
                }
            }
        }
    })


    print limit.evaluate({
        "schema": 1,
        "duration": "PT45M",
        "#duration": "PT45S",
        "starting-comment": "Perry the PLATYPUS",
        "#starting-comment": "Ferb",
        "parting-comment": "Vwl!",
        "#parting-comment": "Vowel!"
    })
