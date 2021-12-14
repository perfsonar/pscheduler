"""
Limit Class for test-type
"""

from ...jsonval import *
from ...plugins import *
from ...psjson import *


test_data_validator = {
    "type": "object",
    "properties": {
        "test": { "$ref": "#/pScheduler/String" },
        "limit": { "$ref": "#/pScheduler/AnyJSON" }
    },
    "additionalProperties": False,
    "required": [ "test", "limit" ]
}

def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return json_validate(data, test_data_validator)



class LimitTest(object):

    """Limit that passes or fails based on whether or not a test says it
    does.
    """

    def __init__(self,
                 data   # Data suitable for this class
                 ):

        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.test = data['test']
        self.limit = data['limit']

        returncode, stdout, stderr = plugin_invoke(
            "test", self.test, "limit-is-valid",
            stdin = json_dump(self.limit),
            # TODO:  Is this reasonable?
            timeout = 5
            )

        if returncode != 0:
            raise RuntimeError("Failed to validate limit: %s" % stderr)

        result = json_load(stdout, max_schema=1)
        if not result['valid']:
            raise ValueError("Invalid limit: %s" % result['error'])


    def checks_schedule(self):
        return False


    def evaluate(self,
                 proposal  # Task and hints
                 ):

        # Dissent if the test isn't our type

        if proposal["task"]["test"]["type"] != self.test:
            return { "passed": False, "reasons": [ "Test is not '%s'" % self.test ] }

        pass_input = {
            "spec": proposal["task"]["test"]["spec"],
            "limit": self.limit
            }

        returncode, stdout, stderr = plugin_invoke(
            "test", self.test, "limit-passes",
            stdin = json_dump(pass_input),
            # TODO:  Is this reasonable?
            timeout = 5
            )

        if returncode != 0:
            raise RuntimeError("Failed to validate limit: %s" % stderr)

        check_result = json_load(stdout, max_schema=1)
        passed = check_result["passes"]

        result = {
            "passed": passed,
            "limit": self.limit
        }
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


    print(json_dump(limit.evaluate(
        {
            "task": {
                "test": {
                    "type": "idle",
                    "spec": {
                        "schema": 1,
                        "#duration": "PT45M",
                        "duration": "PT45S",
                        "starting-comment": "Perry the PLATYPUS",
                        "#starting-comment": "Ferb",
                        "#parting-comment": "Vwl!",
                        "parting-comment": "Vowel!"
                    }
                }
            }
        }
    ), pretty=True))
