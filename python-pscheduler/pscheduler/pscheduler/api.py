"""
Functions related to the pScheduler REST and Plugin APIs
"""

import socket
import urlparse
import uuid

def api_root():
    "Return the standard root location of the pScheduler hierarchy"
    return '/pscheduler'

def api_this_host():
    "Return a fully-qualified name for this host"
    return socket.getfqdn()


def api_url(host = None,
            path = None,
            port = None,
            protocol = 'https'
            ):
    """Format a URL for use with the pScheduler API."""

    # IPv6 addresses get special treatment
    try:
        socket.inet_pton(socket.AF_INET6, host)
        host = "[%s]" % host
    except socket.error:
        pass  # Not an IPv6 address.

    if path is not None and path.startswith('/'):
        path = path[1:]
    return protocol + '://' \
        + (api_this_host() if host is None else str(host)) \
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


if __name__ == "__main__":
    print api_url()
    print api_url(protocol='https')
    print api_url(host='host.example.com')
    print api_url(host='host.example.com', path='/both-slash')
    print api_url(host='host.example.com', path='both-noslash')
    print api_url(path='nohost')
    print
    print api_full_host()
