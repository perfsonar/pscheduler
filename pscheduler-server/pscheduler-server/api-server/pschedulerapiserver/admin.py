#
# Administrative Information
#

import datetime
import pscheduler
import pytz
import socket
import time
import tzlocal
import werkzeug

from pschedulerapiserver import application

from .access import *
from .args import arg_integer
from .dbcursor import dbcursor_query
from .response import *
from .util import *
from .log import log

@application.route("/", methods=['GET'])
def root():
    return ok_json("This is the pScheduler API server on %s (%s)."
                   % (server_hostname(), pscheduler.api_local_host_name()),
                   sanitize=False)



max_api = 4


@application.route("/api", methods=['GET'])
def api():
    return ok_json(max_api, sanitize=False)


@application.before_request
def before_req():
    log.debug("REQUEST: %s %s", request.method, request.url)

    try:
        version = arg_integer("api")
        if version is None:
            version = 1
        if version > max_api:
            return not_implemented(
                "No API above %s is supported" % (max_api))
    except ValueError as ex:
        return bad_request("Invalid API value '%s': %s" %(arg_string("api"), str(ex)))

    # All went well.
    return None


@application.errorhandler(Exception)
def exception_handler(ex):

    if isinstance(ex, werkzeug.exceptions.NotFound):
        return not_found()

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
    return ok_json(pscheduler.api_local_host_name(), sanitize=False)


@application.route("/schedule-horizon", methods=['GET'])
def schedule_horizon():
    """Get the length of the server's scheduling horizon"""

    cursor = dbcursor_query(
        "SELECT schedule_horizon FROM configurables", onerow=True)

    return ok_json(pscheduler.timedelta_as_iso8601(cursor.fetchone()[0]),
                   sanitize=False)


@application.route("/clock", methods=['GET'])
def clock():
    """Return clock-related information"""

    try:
        return ok_json(pscheduler.clock_state(), sanitize=False)
    except Exception as ex:
        return error("Unable to fetch clock state: " + str(ex))


@application.route("/mtu-safe", methods=['GET'])
def mtu_safe():
    """Return JSON indicating whether MTU to destination is safe"""
    dest = arg_string("dest")
    if dest is None:
        return bad_request("Missing destination")

    try:
        (status, message) = pscheduler.mtu_path_is_safe(dest)
        return ok_json(
            { "safe": status, "message": message },
            sanitize=False)

    except Exception as ex:
        log.exception()
        return error(str(ex))


@application.route("/status", methods=['GET'])
def get_status():
    response = {}

    response["time"] = pscheduler.datetime_as_iso8601(pscheduler.time_now())

    # Get the heartbeat status
    try:
        services = dbcursor_query("SELECT * FROM heartbeat_json", onerow=True).fetchone()[0]
    except Exception:
        services = {}

    # Add the database status
    try:
        # query database, calculate server run time
        cursor = dbcursor_query("SELECT extract(epoch from current_timestamp - pg_postmaster_start_time())", onerow=True)
        time_val = pscheduler.seconds_as_timedelta(cursor.fetchone()[0])
        response["services"]["database"] = { "uptime": str(pscheduler.timedelta_as_iso8601(time_val))  }
    except Exception:
        pass

    response["services"] = services
        
    runs = {}
    # query database for last run information
    try:
        cursor = dbcursor_query("SELECT times_actual FROM run WHERE state=run_state_finished()")
        times = cursor.fetchall()
        formatted = []
        for val in times:
            formatted.append(val[0].upper)
        runs["last-finished"] = str(pscheduler.datetime_as_iso8601(max(formatted)))
    except Exception:
        # handles empty result and faulty query
        runs["last-finished"] = None

    # query database for last scheduled information
    try:
        cursor = dbcursor_query("SELECT added FROM run")
        times = cursor.fetchall()
        formatted = []
        for val in times:
            formatted.append(val[0])
        runs["last-scheduled"] = str(pscheduler.datetime_as_iso8601(max(formatted)))
    except Exception:
        # handles empty result and faulty query
        runs["last-scheduled"] = None    

    response["runs"] = runs

    return ok_json(response, sanitize=False)
