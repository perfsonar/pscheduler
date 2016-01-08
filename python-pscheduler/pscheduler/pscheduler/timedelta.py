#
# Utilities for dealing with timedeltas
#

def timedelta_as_seconds(timedelta):
    """Return the number of seconds in an interval.  Note that this does
    not include months or years."""
    # TODO: Callers should use timedelta.total_seconds() when Py2.7 becomes standard fare.
    return ((timedelta.days * 86400 + timedelta.seconds)*10**6 +
            timedelta.microseconds) / 10**6


def timedelta_is_zero(timedelta):
    return (timedelta.days == 0) \
        and (timedelta.seconds == 0) \
        and (timedelta.microseconds == 0)
