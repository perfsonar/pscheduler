"""
Class for doing enumerated matches
"""


from jsonval import json_validate


class EnumMatcher():

    "Class that matches an enumeration."

    def __init__(self, enum):
        """Construct a matcher.  The 'enum' argument is a dict that conforms to
        an EnumMatch as described in the pScheduler JSON Style Guide
        and Type Dictionary.
        """
        valid, message = json_validate(enum,
                                       { "type": "object",
                                         "properties": {
                                             "enumeration": { "$ref": "#/pScheduler/EnumMatch" }
                                         },
                                         "additionalProperties": False
                                         })

        if not valid:
            raise ValueError("Invalid match: " + message)

        try:
            self.invert = enum["invert"]
        except KeyError:
            self.invert = False

        self.enum = enum["enumeration"]

    def __contains(self, enum):
        """
        Scan each element in the input enumeration and make sure
        that each element shows up in our allowed enumeration
        """
        for element in enum:
            if element not in self.enum:
                return False

        return True

    def contains(self, enum):
        "Try to match a candidate enum and return a Boolean"

        # allow matching a single item or a list
        if not isinstance(enum, list):
            enum = [enum]

        result = self.__contains(enum)
        return not result if self.invert else result


# Test program

if __name__ == "__main__":

    matcher = EnumMatcher({
        "enumeration": ["foo", "bar", "biz"],
        "invert": False
    })

    for enum in [["foo"],
                 ["foo", "bar"],
                 ["foo", "notallowed", "biz"]]:
        print enum, matcher.contains(enum)
