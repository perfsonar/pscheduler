"""
Functions related to the pScheduler REST and Plugin APIs
"""

import socket
import urlparse
import uuid

from .psdns import *
from .psurl import *


def api_root():
    "Return the standard root location of the pScheduler hierarchy"
    return '/pscheduler'

def api_this_host():
    "Return a fully-qualified name for this host"
    return socket.getfqdn()


def __host_per_rfc_2732(host):
    "Format a host name or IP for a URL according to RFC 2732"

    try:
        socket.inet_pton(socket.AF_INET6, host)
        return "[%s]" % (host)
    except socket.error:
        return host  # Not an IPv6 address


def api_replace_host(url_text, replacement):
    "Replace the host portion of a URL"

    url = list(urlparse.urlparse(url_text))
    url[1] = __host_per_rfc_2732(replacement)
    return urlparse.urlunparse(url)



def api_url(host = None,
            path = None,
            port = None,
            protocol = 'https'
            ):
    """Format a URL for use with the pScheduler API."""

    host = api_this_host() if host is None else str(host)
    host = __host_per_rfc_2732(host)

    if path is not None and path.startswith('/'):
        path = path[1:]
    return protocol + '://' \
        + host \
        + ('' if port is None else (':' + str(port))) \
        + api_root() + '/'\
        + ('' if path is None else str(path))




def api_is_task(url):
    """Determine if a URL looks like a valid task URL"""
    # Note that this generates an extra array element because of the
    # leading slash.
    url_parts = urlparse.urlparse(url).path.split('/')

    if len(url_parts) != 4 \
            or (url_parts[:3] != ['', 'pscheduler', 'tasks' ]):
        return False

    try:
        uuid.UUID(url_parts[3])
    except ValueError:
        return False

    return True



def api_is_run(url):
    """Determine if a URL looks like a valid run URL"""
    # Note that this generates an extra array element because of the
    # leading slash.
    url_parts = urlparse.urlparse(url).path.split('/')
    if len(url_parts) != 6 \
            or (url_parts[:3] != ['', 'pscheduler', 'tasks' ]) \
            or (url_parts[4] != 'runs'):
        return False

    try:
        uuid.UUID(url_parts[3])
        uuid.UUID(url_parts[5])
    except ValueError:
        return False

    return True


def api_result_delimiter():
    """
    Return the delimiter to be used by background tests when producing
    multiple results.
    """
    return "---- pScheduler End Result ----"



#
# TODO: Remove this when the backward-compatibility code is removed
#

def api_has_pscheduler(host, timeout=5):
    """
    Determine if pScheduler is running on a host
    """
    # Null implies localhost
    if host is None:
        host = "localhost"

    # Make sure the address resolves, otherwise url_get will return
    # non-200.

    resolved = None
    for ip_version in [ 4, 6 ]:
        resolved = pscheduler.dns_resolve(host,
                                          ip_version=ip_version,
                                          timeout=timeout)
        if resolved:
            break

    if not resolved:
        return False
 
    status, raw_spec = pscheduler.url_get(pscheduler.api_url(resolved),
                                          timeout=timeout, throw=False)

    return status == 200



from contextlib import closing

def api_has_bwctl(host):
    """
    Determine if a host is running the BWCTL daemon
    """
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(3)
            return sock.connect_ex((host, 4823)) == 0
    except:
        pass
    try:
        with closing(socket.socket(socket.AF_INET6, socket.SOCK_STREAM)) as sock:
            sock.settimeout(3)
            return sock.connect_ex((host, 4823)) == 0
    except:
        return False



if __name__ == "__main__":
    print api_url()
    print api_url(protocol='https')
    print api_url(host='host.example.com')
    print api_url(host='host.example.com', path='/both-slash')
    print api_url(host='host.example.com', path='both-noslash')
    print api_url(path='nohost')
    print
    print api_full_host()

    print api_has_bwctl(None)
    print api_has_pscheduler(None)
