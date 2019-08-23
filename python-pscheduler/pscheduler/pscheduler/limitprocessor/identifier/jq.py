"""
Identifier Class for jq
"""

from ...jsonval import *
from ...jqfilter import *

JQ_DATA_VALIDATOR = {
    "$ref": "#/pScheduler/JQTransformSpecification"
}


def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """

    return json_validate(data, JQ_DATA_VALIDATOR)



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

        self.jqfilter = JQFilter(
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
