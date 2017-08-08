"""
Identifier Class for jq
"""

import pscheduler

# Note that this is done with a string because we don't support args
# or raw output here.
jq_data_validator = {
    "type": "object",
    "properties": {
        "transform": { "$ref": "#/pScheduler/JQTransformSpecification" },
    },
    "additionalProperties": False,
    "required": [ "transform" ]
}


def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """

    return pscheduler.json_validate(data, jq_data_validator)



class IdentifierJQ():


    """
    Class that holds and processes identifiers
    """


    def __init__(self,
                 data   # Data suitable for this class
                 ):

        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.jqfilter = pscheduler.JQFilter(
            data["transform"]["script"],
            args=data["transform"].get("args", {}),
            output_raw=data["transform"].get("output-raw", False)
        )



    def evaluate(self,
                 hints  # Information used for doing identification
                 ):

        """Given a set of hints, evaluate this identifier and return True if
        an identification is made.
        """

        try:
            returned = self.jqfilter(hints)[0]
        except Exception as ex:
            return False

        if type(returned) == bool:
            return returned

        # At this point, there's no usable date.  Don't identify.
        return False



if __name__ == "__main__":

    data = {
        "transform": {
            "script": ".server == $address",
            "args": {
                "address": "10.0.0.7"
            }
        }
    }

    jqid = IdentifierJQ(data)

    print jqid.evaluate({
        "requester": "10.0.0.7",
        "server": "10.0.0.8",
        })
