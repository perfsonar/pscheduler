#
# Utility Functions
#

import socket
import urlparse

from flask import request


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



#
# Hostnames
#

def server_fqdn():
    """
    Figure out the name of the server end of the request, punting if it's
    the local host or not available.
    """

    request_netloc = urlparse.urlparse(request.url_root).netloc.split(':')[0]

    my_addr = request.environ.get("SERVER_ADDR", None)
    if my_addr is None:
        return request_netloc
    my_fqdn = socket.getfqdn(my_addr)

    if my_fqdn == request_netloc:
        return request_netloc

    return my_fqdn


       

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
