"""
Range of durations
"""

import datetime

from .iso8601 import *
from .jsonval import *


class DurationRange():

    "Range of durations"

    def __init__(self, drange):
        """Construct a range from a JSON DurationRange."""

        # TODO: Would be nice if this class could treat missing
        # lower/upper as zero or infinity.

        # TODO: Figure out why this can't just point to a DurationRange

        valid, message = json_validate(drange, {
            "type": "object",
            "properties": {
                "lower": {"$ref": "#/pScheduler/Duration"},
                "upper": {"$ref": "#/pScheduler/Duration"}
            },
            "additionalProperties": False,
            "required": ["lower", "upper"]
        })

        if not valid:
            raise ValueError("Invalid duration range: %s" % message)

        self.lower_str = drange['lower']
        self.lower = iso8601_as_timedelta(self.lower_str)
        self.upper_str = drange['upper']
        self.upper = iso8601_as_timedelta(self.upper_str)

    def __contains__(self, duration):
        """See if the range contains the specified duration, which can be a
        timedelta or ISO8601 string."""

        if isinstance(duration, datetime.timedelta):
            test_value = duration
        elif isinstance(duration, str):
            test_value = iso8601_as_timedelta(duration)
        else:
            raise ValueError(
                "Invalid duration; must be ISO8601 string or timedelta.")

        return self.lower <= test_value <= self.upper

    def contains(self, duration, invert=False):
        """Like __contains__, but can do inversion and returns a message stub

        Return value is (contains, stub), where 'contains' is a boolean
        and 'stub' describes why the check failed (e.g., "is not in PT1M..PT1H")
        """

        in_range = duration in self

        if (in_range and invert) or (not in_range and not invert):
            return False, ("not %s %s..%s" %
                           ("outside" if invert else "in",
                            self.lower_str, self.upper_str))

        return True, None


# Test program

if __name__ == "__main__":

    drange = DurationRange({
        "lower": "PT10S",
        "upper": "PT1M"
    })

    for value in ["PT1S",
                  datetime.timedelta(seconds=3),
                  "PT30S",
                  datetime.timedelta(seconds=45),
                  "PT1M",
                  "PT5M",
                  datetime.timedelta(minutes=10)
                  ]:
        result = value in drange
        print(value, result)
        for invert in [False, True]:
            print("%s Invert=%s %s" % (value, invert,
                                       drange.contains(value, invert=invert)))
        print()
