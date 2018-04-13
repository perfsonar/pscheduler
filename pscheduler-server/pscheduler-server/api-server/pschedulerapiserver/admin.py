#
# Administrative Information
#

import datetime
import pscheduler
import psutil
import pytz
import socket
import time
import tzlocal

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
              % (server_hostname(), pscheduler.api_this_host()))



max_api = 4


@application.route("/api", methods=['GET'])
def api():
    return ok_json(max_api)


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
    except ValueError:
        return bad_request("Invalid API value.")

    # All went well.
    return None


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
def clock():
    """Return clock-related information"""

    try:
        return ok_json(pscheduler.clock_state())
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
        return ok_json({
            "safe": status,
            "message": message
            })
    except Exception as ex:
        log.exception()
        return error(str(ex))

@application.route("/status", methods=['GET'])
def get_status():
    response = {}

    response["time"] = str(pscheduler.datetime_as_iso8601(datetime.datetime.now()))

    # query process table
    services = {}
    items = ["scheduler", "archiver", "ticker", "runner", "database"]
    for proc in psutil.process_iter():
	pinfo = proc.as_dict(attrs=['name', 'create_time'])
        if (pinfo["name"] in items):
            # calculate elapsed running time
            running_time = pscheduler.seconds_as_timedelta(time.time() - pinfo["create_time"])
            services[pinfo["name"]] = { "running": True, "time": str(pscheduler.timedelta_as_iso8601(running_time)) }
            items.remove(pinfo["name"])
    try:
        # query database, calculate server run time
        cursor = dbcursor_query("SELECT extract(epoch from current_timestamp - pg_postmaster_start_time())", onerow=True)
    	time_val = pscheduler.seconds_as_timedelta(cursor.fetchone()[0])
	services["database"] = { "running": True, "time": str(pscheduler.timedelta_as_iso8601(time_val))  }
	items.remove("database")
    except Exception as ex:
	pass
    
    if len(items) > 0:
        # there are daemons that aren't running
        for item in items:
            services[item] = { "running": False }

    response["services"] = services    
    
    # query database for last run information
    runs = {}
    cursor = dbcursor_query("SELECT times_actual FROM run WHERE state=5")
    times = cursor.fetchall() 
    formatted = []
    for val in times:
        formatted.append(val[0].upper)
    runs["last-finished"] = str(pscheduler.datetime_as_iso8601(max(formatted)))
   
    # query database for last scheduled information
    cursor = dbcursor_query("SELECT added FROM run")
    times = cursor.fetchall()
    formatted = []
    for val in times:
        formatted.append(val[0])
    runs["last-scheduled"] = str(pscheduler.datetime_as_iso8601(max(formatted)))

    response["runs"] = runs

    return ok_json(response)

