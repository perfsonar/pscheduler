#
# Utilities for dealing with times
#
# TODO: Rename this to 'time.py'
#

import datetime

from dateutil.tz import tzlocal

   

#
# Timedelta
#

def seconds_as_timedelta(seconds):
    """Return an absolute number of seconds converted to a timedelta"""
    return datetime.timedelta(seconds=seconds)

def timedelta_as_seconds(timedelta):
    """Return the number of seconds in an interval.  Note that this does
    not include months or years."""
    # TODO: Callers should use timedelta.total_seconds() when Py2.7 becomes standard fare.
    return ((timedelta.days * 86400 + timedelta.seconds)*10**6 +
            timedelta.microseconds) / (10.0**6)


def timedelta_is_zero(timedelta):
    return (timedelta.days == 0) \
        and (timedelta.seconds == 0) \
        and (timedelta.microseconds == 0)




#
# Time in General
#

def time_now():
    """
    Return the time in the current time zone
    """
    return datetime.datetime.now(tzlocal())


def time_until(when):
    """
    Calculate the time until a given time and return a timedelta.  If
    the time specified is in the past, return no time.
    """

    if type(when) != datetime.datetime:
        raise ValueError("Not passed a datetime")
    
    now = time_now()
    if when < now:
        return datetime.timedelta()
    return when - now



def time_until_seconds(when):
    """
    Calculate the time until a given time and return seconds.  If the
    time specified is in the past, return zero.
    """

    return timedelta_as_seconds(time_until(when))
