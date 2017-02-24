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
from .util import *
from .log import log

@application.route("/", methods=['GET'])
def root():
    return ok_json("This is the pScheduler API server on %s (%s)."
              % (server_fqdn(), pscheduler.api_this_host()))


@application.route("/api", methods=['GET'])
def api():
    return ok_json(1)


@application.before_request
def before_req():
    log.debug("REQUEST: %s %s", request.method, request.url)


@application.errorhandler(Exception)
def exception_handler(ex):
    log.exception()
    return error("Internal problem; see system logs.")


@application.route("/exception", methods=['GET'])
def exception():
    """Throw an exception"""
    # Allow only from localhost
    if not request.remote_addr in ['127.0.0.1', '::1']:
        return not_allowed()

    raise Exception("Forced exception.")


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
