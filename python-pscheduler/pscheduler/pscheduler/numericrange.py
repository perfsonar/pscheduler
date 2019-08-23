"""
Range of numeric values
"""

from .jsonval import *
from .psjson import *
from .sinumber import *

class NumericRange():

    "Range of numbers"

    def __init__(self, nrange):
        """Construct a range from a JSON NumericRange."""

        # TODO: Would be nice if this class could treat missing
        # lower/upper as -/+ infinity.

        # TODO: Figure out why this can't just point to a NumericRange

        valid, message = json_validate(nrange, {
            "type": "object",
            "properties": {
                "lower": {"$ref": "#/pScheduler/Numeric"},
                "upper": {"$ref": "#/pScheduler/Numeric"}
            },
            "additionalProperties": False,
            "required": ["lower", "upper"]
        })

        if not valid:
            raise ValueError("Invalid numeric range: %s" % message)

        lower = nrange['lower']
        if isinstance(lower, str):
            self.lower = si_as_number(lower)
        else:
            self.lower = lower
        self.lower_str = str(lower)

        upper = nrange['upper']
        if isinstance(upper, str):
            self.upper = si_as_number(upper)
        else:
            self.upper = upper
        self.upper_str = str(upper)

    def __contains__(self, number):
        """See if the range contains the specified number, which can be any Numeric."""

        if isinstance(number, float):
            test_value = number
        else:
            test_value = si_as_number(number)

        return self.lower <= test_value <= self.upper

    def contains(self, number, invert=False):
        """Like __contains__, but can do inversion and returns a message stub

        Return value is (contains, stub), where 'contains' is a boolean
        and 'stub' describes why the check failed (e.g., "is not in PT1M..PT1H")
        """

        in_range = number in self

        if (in_range and invert) or (not in_range and not invert):
            return False, ("not %s %s..%s" %
                           ("outside" if invert else "in",
                            self.lower_str, self.upper_str))

        return True, None


# Test program

if __name__ == "__main__":

    nrange = NumericRange({
        "lower": 3.14,
        "upper": "100K"
    })

    for value in [
        1,
        6.78,
        "10K",
        "100K",
        "1M"
    ]:
        result = value in nrange
        print(value, result)
        for invert in [False, True]:
            print("%s Invert=%s %s" % (value, invert,
                                       nrange.contains(value, invert=invert)))
        print()
