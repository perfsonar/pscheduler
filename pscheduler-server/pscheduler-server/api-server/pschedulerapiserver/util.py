#
# Utility Functions
#

import socket
import urllib
import uuid

from flask import request

from .args import *
from .response import *


#
# API
#

def requested_api():
    """
    Get the requested API, raising a ValueError if it's not valid
    """

    try:
        api = arg_integer("api")
    except ValueError as ex:
        raise ValueError(f'Invalid API value {arg_string("api")}: {str(ex)}')
    if api is None:
        api = 1
    return api



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
