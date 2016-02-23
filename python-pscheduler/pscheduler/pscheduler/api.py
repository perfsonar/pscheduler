"""
Functions relates to the pScheduler REST API
"""


def api_url(host = '127.0.0.1',  # 'localhost' isn't guaranteed to resolve.
            path = None,
            port = 29285
            ):
    if path is not None and path.startswith('/'):
        path = path[1:]
    return 'http://' \
        + host \
        + (':' + str(port) if port is not None else '') \
        + ('/' + path if path is not None else '')

if __name__ == "__main__":
    print api_url()
    print api_url(host='host.example.com')
    print api_url(host='host.example.com', path='/both-slash')
    print api_url(host='host.example.com', path='both-noslash')
    print api_url(path='nohost')
