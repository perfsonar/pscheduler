#
# Utilities for the ping tool
#

import datetime
import pscheduler

def ping_tool_duration(spec):
    """
    Calculate how long ing should take to run
    """

    total = datetime.timedelta()

    count = int(spec.get('count', 5))

    try:
        interval = pscheduler.iso8601_as_timedelta(spec['interval'])
    except KeyError:
        interval = datetime.timedelta(seconds=1)

    if count > 1:
        # We do one less because there's no wait interval after the last
        # packet other than the timeout.
        total += (count - 1) * interval

    # Stick one timeout on the end, which comes from waiting for
    # the last packet.
    try:
        timeout = pscheduler.iso8601_as_timedelta(spec['timeout'])
    except KeyError:
        timeout = datetime.timedelta(seconds=2)
    total += timeout


    # A deadline overrides everything we've calculated so far.

    try:
        total =  pscheduler.iso8601_as_timedelta(spec['deadline'])
    except KeyError:
        pass  # No deadline is just fine.

    # Finish up with a little bit of slop
    total += datetime.timedelta(seconds=1)

    return total


def ping_test_duration(spec):
    """
    Return the total time for a test and processing afterward to run
    """

    total = ping_tool_duration(spec)
    
    #
    # DNS Resolution
    #

    try:
        hostnames = spec['hostnames']
    except KeyError:
        hostnames = True

    # Some time for DNS, which will be done in parallel.
    # TODO: Should probably ask the DNS module for the timeout.
    if hostnames:
        total += datetime.timedelta(seconds=2)

    #
    # Slop
    #

    total += datetime.timedelta(seconds=1)

    return total
