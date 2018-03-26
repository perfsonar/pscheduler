#
# Utility Functions
#

import socket
import urlparse
import uuid

from flask import request

from dbcursor import *


#
# Hints
#

def request_hints():
    result = {
        "requester": request.remote_addr
    }

    # This handles things cross-platform with Apache first.
    for var in [ "SERVER_ADDR", "LOCAL_ADDR" ]:
        value = request.environ.get(var, None)
        if value is not None:
            result["server"] = value
            break

    return result




def task_requester_key(task_uuid):
    """
    Get the requester and key for a task from its hints.

    Return None if the task doesn't exist or has no requester hint.
    """

    with dbcursor_query(
        "SELECT hints, json ->> '_key' FROM task WHERE uuid = %s", [task_uuid]
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

    return urlparse.urlparse(request.url_root).hostname


def server_netloc():
    """
    Figure out the netloc of the server end of the request, punting if it's
    the local host or not available.
    """

    return urlparse.urlparse(request.url_root).netloc


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
    result = urlparse.urlparse(url)
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
