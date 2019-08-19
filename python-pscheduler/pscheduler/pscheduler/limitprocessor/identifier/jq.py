"""
Identifier Class for jq
"""

import pscheduler

JQ_DATA_VALIDATOR = {
    "$ref": "#/pScheduler/JQTransformSpecification"
}


def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """

    return pscheduler.json_validate(data, JQ_DATA_VALIDATOR)



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
            data["script"],
            args=data.get("args", {}),
            output_raw=data.get("output-raw", False)
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

        if isinstance(returned, bool):
            return returned

        # At this point, there's no usable date.  Don't identify.
        return False



if __name__ == "__main__":

    data = {
        "script": ".server == $address",
        "args": {
            "address": "10.0.0.7"
        }
    }

    jqid = IdentifierJQ(data)

    print(jqid.evaluate({
        "requester": "10.0.0.7",
        "server": "10.0.0.8",
        }))
