#
# Administrative Information
#

import pscheduler
import socket

from pschedulerapiserver import application

from .dbcursor import dbcursor
from .response import *
from .url import *


@application.route("/", methods=['GET'])
def root():
    return ok("This is the pScheduler API server on %s.\n"
              % socket.gethostname())


@application.route("/hostname", methods=['GET'])
def hostname():
    """Return the hosts's name"""
    return ok_json(pscheduler.api_this_host())


@application.route("/schedule-horizon", methods=['GET'])
def schedule_horizon():
    """Get the length of the server's scheduling horizon"""
    dbcursor().execute("SELECT schedule_horizon FROM configurables")
    # TODO: Assert that rowcount is 1
    return ok_json(pscheduler.timedelta_as_iso8601(cursor.fetchone()[0]))


@application.route("/time", methods=['GET'])
def time():
    """Return clock-related information"""

    result = {
        # TODO: This needs to show fractional seconds.
        'time': pscheduler.datetime_as_iso8601(pscheduler.time_now()),
        # TODO: The next four lines are dummied up.
        'sync': False,
        'accuracy': 0.060,
        'method': 'ntp',
        'message': "THIS IS DUMMY DATA\nsynchronised to NTP server (97.107.128.58) at stratum 3\n    time correct to within 60 ms\n   polling server every 1024 s"

        }
    return ok_json(result)
