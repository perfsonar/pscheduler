#
# Utilities for sleeping
#

import datetime
import time

from .iso8601 import iso8601_as_datetime
from .pstime import time_until_seconds


def sleep_until(when):
    """
    Sleep until a time specified by a datetime or an ISO 8601 string.
    If the time specified has passed, just return.
    """

    if type(when) == str:
        when = iso8601_as_datetime(when)

    if type(when) != datetime.datetime:
        raise ValueError("Passed wrong type; must be string or datetime")

    how_long = time_until_seconds(when)
    time.sleep(how_long)
