"""
Functions for dealing with ISO 8601 timestamps and intervals
"""

import isodate

from tzlocal import get_localzone


def iso8601_as_timedelta(iso):
    """Convert an ISO 8601 string to a timdelta"""
    try:
        return isodate.parse_duration(iso)
    except isodate.isoerror.ISO8601Error:
        # TODO: Throw a ValueError?
        return None


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
        print ex
        # TODO: Throw a ValueError?
        return None

# TODO: This function exists in datetime as .isoformat()
def datetime_as_iso8601(datetime):
    return isodate.datetime_isoformat(datetime)
