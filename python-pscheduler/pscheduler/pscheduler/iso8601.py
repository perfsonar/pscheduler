"""
Functions for dealing with ISO 8601 timestamps and intervals
"""

import isodate

def iso8601_as_timedelta(iso):
    """Convert an ISO 8601 string to a timdelta"""
    try:
        return isodate.parse_duration(iso)
    except isodate.isoerror.ISO8601Error:
        # TODO: Throw a ValueError?
        return None


def timedelta_as_iso8601(timedelta):
    return isodate.duration_isoformat(timedelta)


def iso8601_as_datetime(iso):
    try:
        return isodate.parse_datetime(iso)
    except isodate.isoerror.ISO8601Error:
        # TODO: Throw a ValueError?
        return None


# TODO: This function exists in datetime as .isoformat()
def datetime_as_iso8601(datetime):
    return isodate.datetime_isoformat(datetime)
