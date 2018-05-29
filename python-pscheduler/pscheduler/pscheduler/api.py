"""
Functions related to the pScheduler REST and Plugin APIs
"""

import multiprocessing
import multiprocessing.dummy
import socket
import threading
import urlparse
import uuid

# HACK: BWCTLBC
import os


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
    if replacement is not None:
        url[1] = __host_per_rfc_2732(replacement)
    return urlparse.urlunparse(url)




def api_url(host = None,
            path = None,
            port = None,
            protocol = None
            ):
    """Format a URL for use with the pScheduler API."""

    host = 'localhost' if host is None else str(host)
    # Force the host into something valid for DNS
    # See http://stackoverflow.com/a/25103444/180674
    try:
        host = host.encode('idna')
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
        parsed=urlparse.urlparse("bogus://%s" % (formatted_host))
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



def api_ping(host, bind=None, timeout=3):
    """
    See if an API server is alive within a given timeout.  If 'host'
    is None, ping the local server.

    Returns a tuple of (up, reason), where reason is a string
    explaining why 'up' is what is is.
    """
    if host is None:
        host = api_this_host()

    url = pscheduler.api_url(host)

    status, result = url_get(url, bind=bind,
                             throw=False, timeout=timeout)

    if status == 200:
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



#
# TODO: Remove this when the backward-compatibility code is removed
#

def api_has_pscheduler(hostport, timeout=5, bind=None):
    """
    Determine if pScheduler is running on a host
    """
    # Null implies localhost
    if hostport is None:
        hostport = "localhost"

    host, port = api_host_port(hostport)


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


    # HACK: BWTCLBC
    # If the environment says to bind to a certain address, do it.
    if bind is None:
        bind = os.environ.get('PSCHEDULER_LEAD_BIND_HACK', None)

    status, raw_spec = pscheduler.url_get(api_url_hostport(hostport),
                                          timeout=timeout,
                                          throw=False,
                                          json=False,
                                          bind=bind # HACK: BWTCLBC
                                          )

    return status == 200



from contextlib import closing


def api_has_bwctl(host, timeout=5, bind=None):
    """
    Determine if a host is running the BWCTL daemon
    """

    # Null implies localhost
    if host is None:
        host = "localhost"

    # HACK: BWTCLBC
    # If the environment says to bind to a certain address, do it.
    if bind is None:
        bind = os.environ.get('PSCHEDULER_LEAD_BIND_HACK', None)

    for family in [socket.AF_INET, socket.AF_INET6]:
        try:
            with closing(socket.socket(family, socket.SOCK_STREAM)) as sock:
                if bind is not None:
                    sock.bind((bind, 0))
                sock.settimeout(timeout)
                return sock.connect_ex((host, 4823)) == 0
        except socket.error:
            pass

    return False



def api_has_services(hosts, timeout=5, bind=None, threads=10):
    """
    Do a parallel rendition of the two functions above.

    Returns a hash of host names and results
    """

    # Work around a bug in 2.6
    # TODO: Get rid of this when 2.6 is no longer in the picture.
    if not hasattr(threading.current_thread(), "_children"):
        threading.current_thread()._children = weakref.WeakKeyDictionary()

    pool = multiprocessing.dummy.Pool(processes=min(len(hosts), threads))

    def check_one(arg):
        host, service, function = arg
        return (host, service, function(host, timeout=timeout, bind=bind))

    args = []
    result = {}
    for host in hosts:
        args.extend([
            (host, "bwctl", api_has_bwctl),
            (host, "pscheduler", api_has_pscheduler)
            ])
        result[host] = {
            "bwctl": None,
            "pscheduler": None
        }


    for host, service, state in pool.imap(check_one, args, chunksize=1):
        result[host][service] = state
    pool.close()
    return result



if __name__ == "__main__":
    print api_url()
    print api_url(protocol='https')
    print api_url(host='host.example.com')
    print api_url(host='host.example.com', path='/both-slash')
    print api_url(host='host.example.com', path='both-noslash')
    print api_url(path='nohost')
    print

    print api_has_bwctl(None)
    print api_has_pscheduler(None)


    print api_has_services(["perfsonardev0.internet2.edu"])
