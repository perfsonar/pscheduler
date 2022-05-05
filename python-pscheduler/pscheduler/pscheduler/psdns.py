"""
Functions for resolving hostnames and IPs
"""

import dns.reversename
import dns.resolver 
import multiprocessing
import multiprocessing.dummy
import os
import queue
import socket
import threading


__DEFAULT_TIMEOUT__ = 2

def dns_default_timeout():
    return __DEFAULT_TIMEOUT__


__VALID_IP_VERSIONS__ = [4, 6, None]
def __check_ip_version__(ip_version):
    if not ip_version in __VALID_IP_VERSIONS__:
        raise ValueError("Invalid IP version '%s'; must be one of % s "
                         % (str(ip_version), __VALID_IP_VERSIONS__))


#
# Single Resolution
#

def __dns_resolve_host(host, ip_version, timeout):
    """
    Resolve a host using the system's facilities
    """
    __check_ip_version__(ip_version)

    if ip_version is None:
        family = 0
    else:
        family = socket.AF_INET if ip_version == 4 else socket.AF_INET6

    def proc(host, family, timing_queue):
        try:
            timing_queue.put(socket.getaddrinfo(host, 0, family))
        except socket.gaierror as ex:
            # TODO: Would be nice if we could isolate just the not
            # found error.
            timing_queue.put([])
        except socket.timeout:
            # Don't care, we just want the queue to be empty if
            # there's an error.
            pass

    timing_queue = queue.Queue()
    thread = threading.Thread(target=proc, args=(host, family, timing_queue))
    thread.setDaemon(True)
    thread.start()
    try:
        results = timing_queue.get(True, timeout)
        if len(results) == 0:
            return None
        family, socktype, proto, canonname, sockaddr = results[0]
    except queue.Empty:
        return None

    # NOTE: Don't make any attempt to kill the thread, as it will get
    # Python all confused if it holds the GIL.

    (ip) = sockaddr
    return str(ip[0])



def dns_resolve(host,
                query=None,
                ip_version=None,
                timeout=__DEFAULT_TIMEOUT__
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
            answers = resolver.query(host, query)
        except (dns.exception.Timeout,
                dns.name.EmptyLabel,
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

    """
    Reverse-resolve a host using the system's facilities
    """

    # TODO: It would be nice of the queue/timeout code wasn't duplicated
    # TODO: Validate 'ip' as an IP and raise a ValueError

    def proc(ip_addr, timing_queue):
        """Process the query"""
        try:
            timing_queue.put(socket.gethostbyaddr(ip_addr)[0])
        except socket.herror:
            timing_queue.put(None)
        except socket.gaierror as ex:
            if ex.errno not in [-2, -5]:
                raise ex
            timing_queue.put(None)

    timing_queue = queue.Queue()
    thread = threading.Thread(target=proc, args=(ip, timing_queue))
    thread.setDaemon(True)
    thread.start()
    try:
        return timing_queue.get(True, timeout)
    except queue.Empty:
        return None

    # NOTE: Don't make any attempt to kill the thread, as it will get
    # Python all confused if it holds the GIL.




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

    __check_ip_version__(ip_version)

    result = {}

    if len(candidates) == 0:
        return result

    pool = multiprocessing.dummy.Pool(
        processes=min(len(candidates), threads) )

    candidate_args = [ (candidate, ip_version) for candidate in candidates ]

    for ip, name in pool.imap(
        __reverser__ if reverse else __forwarder__,
        candidate_args,
        chunksize=1):
        result[ip] = name
    pool.close()
    return result



if __name__ == "__main__":
    print("IPv4:")
    print(dns_resolve('localhost'))
    print(dns_resolve('www.perfsonar.net', ip_version=4))
    print(dns_resolve('www.perfsonar.net', ip_version=4, query='SOA'))
    print(dns_bulk_resolve([
        'www.perfsonar.net',
        'www.es.net',
        'www.geant.org',
        'www.iu.edu',
        'www.internet2.edu',
        'does-not-exist.internet2.edu',
    ], ip_version=4))

    print()
    print("IPv6:")
    print(dns_resolve('www.perfsonar.net', ip_version=6))
    print(dns_bulk_resolve([
        'www.perfsonar.net', 'www.google.com'
    ], ip_version=6))

    print()
    print("Bulk reverse:")
    print(dns_bulk_resolve([
        '127.0.0.1',
        '::1',
        '10.0.0.7',
        '192.168.12.34',
        '8.8.8.8',
        '198.6.1.1',
        '8.8.8.0',
        '2607:f8b0:4002:c06::67',
        'this-is-not-valid'
    ], reverse=True))

    print()
    print("Bulk none:")
    print(dns_bulk_resolve([]))
