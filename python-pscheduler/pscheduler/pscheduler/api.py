"""
Functions relates to the pScheduler REST API
"""



def api_url(host='127.0.0.1', path=''):
    """Get the URL for a path on a given host."""
    if not path.startswith('/'):
        path = '/' + path
    return 'http://' + host + ':29285' + path


if __name__ == "__main__":
    print api_url()
    print api_url(host='host.example.com')
    print api_url(host='host.example.com', path='/both-slash')
    print api_url(host='host.example.com', path='both-noslash')
    print api_url(path='nohost')
