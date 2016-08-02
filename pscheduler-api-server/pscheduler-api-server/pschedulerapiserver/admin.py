#
# Administrative Information
#

import datetime
import pscheduler
import pytz
import socket
import tzlocal

from pschedulerapiserver import application

from .dbcursor import dbcursor_query
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

    try:
        cursor = dbcursor_query(
            "SELECT schedule_horizon FROM configurables", onerow=True)
    except Exception as ex:
        log.exception()
        return error(str(ex))

    return ok_json(pscheduler.timedelta_as_iso8601(cursor.fetchone()[0]))


@application.route("/clock", methods=['GET'])
def time():
    """Return clock-related information"""

    try:
        return ok_json(pscheduler.clock_state())
    except Exception as ex:
        return error("Unable to fetch clock state: " + str(ex))
