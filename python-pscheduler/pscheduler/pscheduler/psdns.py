"""
Functions for resolving hostnames and IPs
"""

import dns.reversename
import dns.resolver
import multiprocessing
import multiprocessing.dummy
import Queue
import socket
import threading

# See Python 2.6 workaround below.

import weakref


__DEFAULT_TIMEOUT__ = 2


def dns_default_timeout():
    return __DEFAULT_TIMEOUT__


def __check_ip_version__(ip_version):
    if ip_version not in [4, 6]:
        raise ValueError("Invalid IP version; must be 4 or 6")


#
# Single Resolution
#

def __dns_resolve_host(host, ip_version, timeout):
    """
    Resolve a host using the system's facilities
    """
    family = socket.AF_INET if ip_version == 4 else socket.AF_INET6

    def proc(host, family, queue):
        try:
            queue.put(socket.getaddrinfo(host, 0, family))
        except socket.gaierror as ex:
            # TODO: Would be nice if we could isolate just the not
            # found error.
            queue.put([])
        except socket.timeout:
            # Don't care, we just want the queue to be empty if
            # there's an error.
            pass

    queue = Queue.Queue()
    thread = threading.Thread(target=proc, args=(host, family, queue))
    # Don't make Python wait for this thread to exit.
    thread.daemon = True
    thread.start()
    try:
        results = queue.get(True, timeout)
        if len(results) == 0:
            return None
        family, socktype, proto, canonname, sockaddr = results[0]
    except Queue.Empty:
        return None

    # NOTE: Don't make any attempt to kill the thread, as it will get
    # Python all confused if it holds the GIL.

    (ip) = sockaddr
    return str(ip[0])


def dns_resolve(host,
                query=None,
                ip_version=4,
                timeout=__DEFAULT_TIMEOUT__,
                ):
    """
    Resolve a hostname to its A record, returning None if not found or
    there was a timeout.
    """
    __check_ip_version__(ip_version)

    if query is None:

        # The default query is for a host,

        return __dns_resolve_host(host, ip_version, timeout)

    else:

        # Any other explicit query value is forced to use DNS.

        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = timeout
            resolver.lifetime = timeout
            if query is None:
                query = 'A' if ip_version == 4 else 'AAAA'
            answers = resolver.query(host, query)
        except (dns.exception.Timeout,
                dns.resolver.NXDOMAIN,
                dns.resolver.NoAnswer,
                dns.resolver.NoNameservers):
            return None

        return str(answers[0])


def dns_resolve_reverse(ip,
                        timeout=__DEFAULT_TIMEOUT__):
    """
    Resolve an IP (v4 or v6) to its hostname, returning None if not
    found or there was a timeout.
    """

    # TODO: Need to also try resolution by local means (/etc/hosts)

    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        revname = dns.reversename.from_address(ip)
        answers = resolver.query(revname, 'PTR')
        return str(answers[0])
    except (dns.exception.Timeout,
            dns.resolver.NXDOMAIN,
            dns.resolver.NoAnswer,
            dns.exception.SyntaxError,
            dns.resolver.NoNameservers):
        return None


#
# Bulk Resolution
#


def __forwarder__(arg):
    """
    Query DNS for (name) and return (name, ip))
    """
    host, ip_version = arg
    return (host, dns_resolve(host, ip_version=ip_version))


def __reverser__(arg):
    """
    Query reverse DNS for (ip) and return (ip, hostname)
    """
    host, ip_version = arg
    return (host, dns_resolve_reverse(host))


def dns_bulk_resolve(candidates, reverse=False, ip_version=None, threads=50):
    """
    Resolve a list of host names to IPs or, if reverse is true, IPs to
    host names.  Return a map of each result keyed to its candidate.

    WARNING: This function will create a pool of up to 'threads'
    threads.
    """

    # This is based loosely on http://stackoverflow.com/a/34377198

    if reverse and ip_version is not None:
        raise ValueError("Unable to force IP version when reverse-resolving")

    if ip_version is None:
        ip_version = 4
    __check_ip_version__(ip_version)

    result = {}

    if len(candidates) == 0:
        return result

    # Work around a bug in 2.6
    # TODO: Get rid of this when 2.6 is no longer in the picture.
    if not hasattr(threading.current_thread(), "_children"):
        threading.current_thread()._children = weakref.WeakKeyDictionary()

    pool = multiprocessing.dummy.Pool(
        processes=min(len(candidates), threads))

    candidate_args = [(candidate, ip_version) for candidate in candidates]

    for ip, name in pool.imap(
            __reverser__ if reverse else __forwarder__,
            candidate_args,
            chunksize=1):
        result[ip] = name
    pool.close()
    return result


if __name__ == "__main__":
    print "IPv4:"
    print dns_resolve('localhost')
    print dns_resolve('www.perfsonar.net', ip_version=4)
    print dns_resolve('www.perfsonar.net', ip_version=4, query='SOA')
    print dns_bulk_resolve([
        'www.perfsonar.net',
        'www.es.net',
        'www.geant.org',
        'www.iu.edu',
        'www.internet2.edu',
        'does-not-exist.internet2.edu',
    ], ip_version=4)

    print "IPv6:"
    print dns_resolve('www.perfsonar.net', ip_version=6)
    print dns_bulk_resolve([
        'www.perfsonar.net',
    ], ip_version=6)

    print "Bulk reverse:"
    print dns_bulk_resolve([
        '192.168.12.34',
        '8.8.8.8',
        '198.6.1.1',
        '8.8.8.0',
        '2607:f8b0:4002:c06::67',
        'this-is-not-valid'
    ], reverse=True)

    print "Bulk none:"
    print dns_bulk_resolve([
    ])
