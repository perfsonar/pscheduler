"""
Functions related to the pScheduler REST API
"""

import socket

def api_root():
    "Return the standard root location of the pScheduler hierarchy"
    return '/pscheduler'


def api_url(host = None,
            path = None,
            port = None,
            protocol = 'http'
            ):
    """Format a URL for use with the pScheduler API."""
    if path is not None and path.startswith('/'):
        path = path[1:]
    return protocol + '://' \
        + (socket.getfqdn() if host is None else str(host)) \
        + ('' if port is None else (':' + str(port))) \
        + api_root() + '/'\
        + ('' if path is None else str(path))

if __name__ == "__main__":
    print api_url()
    print api_url(protocol='https')
    print api_url(host='host.example.com')
    print api_url(host='host.example.com', path='/both-slash')
    print api_url(host='host.example.com', path='both-noslash')
    print api_url(path='nohost')
    print
    print api_full_host()
