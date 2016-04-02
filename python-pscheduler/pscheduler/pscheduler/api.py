"""
Functions related to the pScheduler REST API
"""

def api_root():
    return '/pscheduler'


def api_url(host = None,  # Don't default this.  It breaks 'None' behavior.
            path = None,
            port = None,
            protocol = 'http'
            ):
    if path is not None and path.startswith('/'):
        path = path[1:]
    return protocol + '://' \
        + ('127.0.0.1' if host is None else str(host)) \
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
