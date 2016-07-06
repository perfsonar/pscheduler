"""
Class for doing string matches
"""

import re
import sre_constants

from jsonval import json_validate

class StringMatcher():

    "Class that does several types of string matching."

    def __init__(self, match):

        """Construct a matcher.  The 'match' argument is a dict that conforms to
        a StringMatch as described in the pScheduler JSON Style Guide
        and Type Dictionary.
        """

        # TODO: It seems clunky to have to do this when we should be
        # able to just say { "$ref": "#/pScheduler/StringMatch" } and
        # be done with it.

        valid, message = json_validate({"match": match },
                                       { "type": "object",
                                         "properties": {
                                             "match": { "$ref": "#/pScheduler/StringMatch" }
                                         },
                                         "additionalProperties": False
                                         })

        if not valid:
            raise ValueError("Invalid match: " + message)

        try:
            self.case_insensitive = match["case-insensitive"]
        except KeyError:
            self.case_insensitive = False

        try:
            self.invert = match["invert"]
        except KeyError:
            self.invert = False

        self.style = match["style"]

        if self.style == "regex":
            try:
                self.regex = re.compile(match["match"])
            except sre_constants.error as ex:
                print ex
                raise ValueError("Invalid regular expression: " + str(ex))
        else:
            self.match = match["match"]
            if self.case_insensitive:
                self.match = self.match.lower()


    def __matches(self, string):

        """Do all of the match except the inversion, which wil be done by the
        caller."""

        # TODO: There's probably a more elegant way to do this...

        if self.style == "exact":

            if self.case_insensitive:
                return string.lower() == self.match
            else:
                return string == self.match
        
        elif self.style == "contains":

            if self.case_insensitive:
                return self.match in string.lower()
            else:
                return self.match in string

        elif self.style == "regex":

            if self.case_insensitive:
                matches = self.regex.search(string, re.IGNORECASE)
            else:
                matches = self.regex.search(string)

            return matches is not None

        raise Exception("This should not be reached.")



    def matches(self, string):

        "Try to match a candidate string and return a Boolean"

        result = self.__matches(string)
        return not result if self.invert else result




# Test program

if __name__ == "__main__":

    matcher = StringMatcher({
        "style": "regex",
        "match": "fo+",
        "case-insensitive": False,
        "invert": False
        })

    for string in [ "foo", "bar", "foobar", "bazbarfoo" ]:
        print string, matcher.matches(string)
