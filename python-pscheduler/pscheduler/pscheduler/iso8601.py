"""
Functions for dealing with ISO 8601 timestamps and intervals
"""

import datetime
import isodate

from tzlocal import get_localzone
from dateutil.tz import tzlocal


def iso8601_as_timedelta(iso):
    """Convert an ISO 8601 string to a timdelta"""
    try:
        duration = isodate.parse_duration(iso)
    except isodate.isoerror.ISO8601Error:
        raise ValueError("Invalid ISO duration")
    if not isinstance(duration, datetime.timedelta):
        raise ValueError("Cannot support months or years")
    return duration


def timedelta_as_iso8601(timedelta):
    return isodate.duration_isoformat(timedelta)


def iso8601_as_datetime(iso,
                        localize=False  # Default into local time zone
                        ):
    try:
        parsed = isodate.parse_datetime(iso)
        if localize and parsed.tzinfo is None:
            parsed = get_localzone().localize(parsed)
        return parsed
    except isodate.isoerror.ISO8601Error as ex:
        raise ValueError("Invalid ISO8601 date")


# TODO: This function exists in datetime as .isoformat()
def datetime_as_iso8601(datetime):
    return isodate.datetime_isoformat(datetime)



def iso8601_absrel(when, now=None):
    """
    Return a datetime representing an ISO8601 timestamp (e.g.,
    "2020-09-01T12:34:56-00:00") or a time relative to now as +/- an
    ISO8601 duration (e.g., "+PT34M" or "-P3D").

    If 'now', a datetime, is not none, use that as the current time
    for relative calculations.  This is largely for unit testing.
    """

    if not isinstance(when, str) or len(when) < 2:
        raise ValueError("Invalid timestamp or duration")

    first = when[0]
    if first in [ "+", "-" ]:
        direction = -1 if first == "-" else 1
        if now is None:
            now = datetime.datetime.now(tzlocal())
        if not isinstance(now,datetime.datetime):
            raise ValueError("Invalid now; must be datetime.")
        return now + (iso8601_as_timedelta(when[1:]) * direction)
    else:
        return iso8601_as_datetime(when, localize=True)

