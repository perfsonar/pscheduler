"""
Functions for dealing with ISO 8601 timestamps and intervals
"""

import datetime
import isodate

from tzlocal import get_localzone


def iso8601_as_timedelta(iso):
    """Convert an ISO 8601 string to a timdelta"""
    try:
        duration = isodate.parse_duration(iso)
    except isodate.isoerror.ISO8601Error:
        raise ValueError("Invalid ISO duration")
    if type(duration) != datetime.timedelta:
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
