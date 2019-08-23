"""
Identifier Class for hint
"""

import re
import sre_constants

from ...jsonval import *
from ...stringmatcher import *


data_validator = {
    "type": "object",
    "properties": {
        "hint": { "$ref": "#/pScheduler/String" },
        "match": { "$ref": "#/pScheduler/StringMatch" }
    },
    "required": [ "hint", "match" ]
}

def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return json_validate(data, data_validator)



class IdentifierHint():


    """
    Class that holds and processes "hint" identifiers
    """


    def __init__(self,
                 data   # Data suitable for this class
                 ):

        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.hint = data['hint']
        self.matcher = StringMatcher(data['match'])


    def evaluate(self,
                 hints  # Information used for doing identification
                 ):

        """Given a set of hints, evaluate this identifier and return True if
        an identification is made.

        """

        try:
            value = hints[self.hint]
        except KeyError:
            return False

        return self.matcher.matches(value)



# A short test program

if __name__ == "__main__":

    print("Exact:")
    ident = IdentifierHint({
        "hint": "value",
        "match": {
            "style": "exact",
            "match": "foo",
            "case-insensitive": False
        }
    })

    for value in [ "foo", "bar", "baz" ]:
        print(value, ident.evaluate({ "value": value }))

    print()
    print("Regex:")
    ident = IdentifierHint({
        "hint": "value",
        "match": {
            "style": "regex",
            "match": "(^b|oo$)"
        }
    })

    for value in [ "foo", "bar", "baz", "glorp" ]:
        print(value, ident.evaluate({ "value": value }))

