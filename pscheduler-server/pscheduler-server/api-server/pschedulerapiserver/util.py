#
# Utility Functions
#

import socket
import urllib
import uuid

from flask import request

from .dbcursor import *
from .log import log
from .response import *



#
# Hints
#

def request_hints():

    """Return tuple of (hints, response).  If hints is None, response is a
    response for the caller to return to the requester."""

    result = {}

    # This handles things cross-platform with Apache first.
    for var in [ "SERVER_ADDR", "LOCAL_ADDR" ]:
        value = request.environ.get(var, None)
        if value is not None:
            result["server"] = value
            break

    # If there's no request to proxy the requester address, take the
    # easy way out.

    try:
        requester_header = request.headers["X-pScheduler-Requester"]
    except KeyError:
        result["requester"] = request.remote_addr
        return (result, None)

    # See if the actual requester is allowed to substitute its own address

    try:
        ip, name, key = requester_header.split(";", 3)
    except ValueError:
        return (None, bad_request("Invalid X-pScheduler-Requester header"))

    family, _ip = pscheduler.ip_addr_version(ip, resolve=False)
    if family is None:
        return (None, bad_request("Invalid X-pScheduler-Requester header"))

    # Check the database to see if the name and key are valid

    # Any exceptions here will bubble up and cause the request to
    # fail.

    log.debug("Checking requester key for %s", name)

    with dbcursor_query(
            "SELECT auth_key_is_valid('requester', %s, %s)", [name, key]
    ) as cursor:
        if cursor.rowcount != 1:
            raise Exception("Didn't get expected single row from key validation")
        requester_ok = cursor.fetchone()[0]

    if not requester_ok:
        log.debug("Denied requester proxying for %s", name)
        return (None, forbidden("Requester proxying not allowed"))
    else:
        log.debug("Database says requester key is okay.")

    result["requester"] = ip
    result["requester-proxied-by"] = request.remote_addr

    log.debug("Hints: %s", result)

    return (result, None)




def task_requester_key(task_uuid):
    """
    Get the requester and key for a task from its hints.

    Return None if the task doesn't exist or has no requester hint.
    """

    with dbcursor_query(
        "SELECT hints, participant_key FROM task WHERE uuid = %s", [task_uuid]
    ) as cursor:
        if cursor.rowcount == 0:
            return (None, None)
        elif cursor.rowcount > 1:
            raise Exception("Didn't get expected single row")
        (hints, key) = cursor.fetchone()

    return (hints.get("requester", None), key)



#
# Hostnames
#

def server_hostname():
    """
    Figure out the name of the server end of the request, punting if it's
    the local host or not available.
    """

    return urllib.parse.urlparse(request.url_root).hostname


def server_netloc():
    """
    Figure out the netloc of the server end of the request, punting if it's
    the local host or not available.
    """

    return urllib.parse.urlparse(request.url_root).netloc


#
# URLs
#

def internal_url(path):
    return request.url_root + path

def root_url(path = None):
    return request.url_root + ("" if path is None else path)

def base_url(path = None):
    return request.base_url + ("" if path is None else "/" + path)

def url_last_in_path(url):
    result = urllib.parse.urlparse(url)
    return result.path.split('/')[-1]


#
# UUIDs
#

def uuid_is_valid(test_uuid):
    """
    Determine if a UUID is valid
    """
    try:
        uuid_object = uuid.UUID(test_uuid)
    except ValueError:
        return False
    return True
