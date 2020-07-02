"""
Limit Class for test-type
"""

from ...jsonval import *


testtype_data_validator = {
    "type": "object",
    "properties": {
        "types": {
            "type": "array",
            "items": { "$ref": "#/pScheduler/String" }
        }
    },
    "additionalProperties": False,
    "required": [ "types" ]
}


def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return json_validate(data, testtype_data_validator)



class LimitTestType(object):

    """
    Limit that passes or fails according to a hard-wired value.
    """

    def __init__(self,
                 data   # Data suitable for this class
                 ):

        
        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        # Dodges a reserved word
        self.types = data['types']


    def checks_schedule(self):
        return False


    def evaluate(self,
                 proposal  # Task and hints
                 ):

        """Always return the set value"""

        try:
            if proposal['task']['test']['type'] in self.types:
                return { "passed": True }
        except KeyError:
            return { "passed": False, "reasons": [ "No type in task" ] }

        return { "passed": False, "reasons": [ "Test type not in list" ] }



# A short test program

if __name__ == "__main__":

    limit = LimitTestType({
        "types": [ "rtt", "trace", "latency" ]
    })


    for test in [ "rtt", "trace", "throughput", "bogus" ]:
        print(test, limit.evaluate({ "task": {
            "test": { "type": test }}
                                 }))
