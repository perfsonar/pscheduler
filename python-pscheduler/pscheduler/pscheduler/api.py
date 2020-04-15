"""
Functions related to the pScheduler REST and Plugin APIs
"""

import multiprocessing
import multiprocessing.dummy
import socket
import threading
import urllib
import uuid

from .psdns import *
from .psjson import *
from .psurl import *


def api_root():
    "Return the standard root location of the pScheduler hierarchy"
    return '/pscheduler'

def api_local_host():
    "Return a name that should point to the server on this host."
    return 'localhost'

def api_local_host_fqdn():
    "Return as close to a fully-qualified name for this host as possible."
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

    url = list(urllib.parse.urlparse(url_text))
    if replacement is not None:
        url[1] = __host_per_rfc_2732(replacement)
    return urllib.parse.urlunparse(url)




def api_url(host = None,
            path = None,
            port = None,
            protocol = None
            ):
    """Format a URL for use with the pScheduler API."""

    host = api_local_host() if host is None else str(host)
    # Force the host into something valid for DNS
    # See http://stackoverflow.com/a/25103444/180674
    try:
        host = host.encode('idna').decode("ascii")
    except UnicodeError:
        raise ValueError("Invalid host '%s'" % (host))
    host = __host_per_rfc_2732(host)

    if path is not None and path.startswith('/'):
        path = path[1:]

    if protocol is None:
        protocol = 'https'

    return protocol + '://' \
        + host \
        + ('' if port is None else (':' + str(port))) \
        + api_root() + '/'\
        + ('' if path is None else str(path))



def api_host_port(hostport):
    """Return the host and port parts of a host/port pair"""
    if hostport is None:
        return (None, None)
    formatted_host = __host_per_rfc_2732(hostport)
    try:
        parsed=urllib.parse.urlparse("bogus://%s" % (formatted_host))
        if parsed.port is None: pass #simple test to trigger an error from urlparse on CentOS 6
    except ValueError as ve:
        #TODO: can remove this once we drop CentOS 6
        #python 2.6 urlparse does not properly handle bracketed IPv6, so we do that here
        if "]:" in formatted_host:
            formatted_host = formatted_host.replace("[", "")
            parts = formatted_host.split(']:')
            if len(parts) != 2:
                raise ve
            #convert to int, will raise exception if invalid
            parts[1] = int(parts[1])
            return tuple(parts)
        elif formatted_host.endswith(']'):
            return formatted_host.replace('[',"").replace(']',""), None
        else:
            raise ve
        
    return (None if parsed.hostname == "none" else parsed.hostname,
            parsed.port)


def api_url_hostport(hostport=None,
            path=None,
            protocol=None
            ):
    """Format a URL for use with the pScheduler API where the host name
    may include a port."""
    (host, port) = api_host_port(hostport)
    return api_url(host=host, port=port, path=path, protocol=protocol)



def api_is_task(url):
    """Determine if a URL looks like a valid task URL"""
    # Note that this generates an extra array element because of the
    # leading slash.
    url_parts = urllib.parse.urlparse(url).path.split('/')

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
    url_parts = urllib.parse.urlparse(url).path.split('/')
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



def api_ping(host=None, bind=None, timeout=3):
    """
    See if an API server is alive within a given timeout.  If 'host'
    is None, ping the local server.

    Returns a tuple of (up, reason), where reason is a string
    explaining why 'up' is what is is.
    """
    url = api_url(host)

    status, result = url_get(url, bind=bind, json=False,
                             throw=False, timeout=timeout)

    if status == 200:

        # What came back needs to look like a JSON string or it isn't
        # pScheduler.
        try:
            returned_json = json_load(result)
            if not isinstance(returned_json, str):
                raise ValueError
        except ValueError:
            return (False, "Not running pScheduler")

        return (True, "pScheduler is alive")

    elif status == 400:
        return (False, result)
    elif status in [202, 204, 205, 206, 207, 208, 226,
                    300, 301, 302, 303, 304, 205, 306, 307, 308] \
        or ((status >= 400) and (status <=499)):
        return (False, "Not running pScheduler")

    return (False, "Returned status %d: %s" % (status, result))




def api_ping_list(hosts, bind=None, timeout=None, threads=10):
    """
    Ping a list of hosts and return a list of their statuses.
    """

    if len(hosts) == 0:
        return {}

    # Work around a bug in 2.6
    # TODO: Get rid of this when 2.6 is no longer in the picture.
    if not hasattr(threading.current_thread(), "_children"):
        threading.current_thread()._children = weakref.WeakKeyDictionary()

    pool = multiprocessing.dummy.Pool(processes=min(len(hosts), threads))

    pool_args = [(host, timeout) for host in hosts]
    result = {}

    def ping_one(arg):
        host, timeout = arg
        up, _ = api_ping(host, bind=bind, timeout=timeout)
        return (host, up)

    for host, state in pool.imap(
            ping_one,
            pool_args,
            chunksize=1):
        result[host] = state
    pool.close()
    return result



def api_ping_all_up(hosts, bind=None, timeout=10):
    """
    Determine if all hosts in a list are up.
    """
    results = api_ping_list(hosts, bind=bind, timeout=timeout)

    for host in results:
        if not results[host]:
            return False
    return True



def api_has_pscheduler(hostport, timeout=5, bind=None):
    """
    Determine if pScheduler is running on a host
    """
    # Null implies localhost
    if hostport is None:
        hostport = api_local_host()

    host, port = api_host_port(hostport)


    # Make sure the address resolves, otherwise url_get will return
    # non-200.

    resolved = None

    # DNS: Don't hardwire this.  In fact, this should probably not be
    # done at all.  The url_get will return an error if the host is
    # unresolvable.

    for ip_version in [ 4, 6 ]:
        resolved = dns_resolve(host,
                               ip_version=ip_version,
                               timeout=timeout)
        if resolved:
            break

    if not resolved:
        return False

    status, raw_spec = url_get(api_url_hostport(hostport),
                               timeout=timeout,
                               throw=False,
                               json=False,
                               bind=bind
    )

    return status == 200







if __name__ == "__main__":
    print(api_url())
    print(api_url(protocol='https'))
    print(api_url(host='host.example.com'))
    print(api_url(host='host.example.com', path='/both-slash'))
    print(api_url(host='host.example.com', path='both-noslash'))
    print(api_url(path='nohost'))
    print()

    print(api_ping())
